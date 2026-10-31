/* Host page for the Seafile WOPI editor bridge.
 *
 * Speaks the ArtCraft `?host=parent` postMessage protocol (as merged upstream in
 * WordCraft #3822, GridCraft, PdfCraft, CADCraft):
 *   child -> host : `${app}:ready` {version}
 *                   `${app}:save`  {name, bytes, saveAs, ticket?}
 *                   `${app}:dirty` {dirty}
 *                   `${app}:failed`{error}
 *   host  -> child: `${app}:open`  {name, bytes}
 *                   `${app}:saveResult` {ticket, ok, version?, error?}   (only if the
 *                   editor sent a ticket — upstream bridges do not yet; the lab's RFC)
 *
 * The WOPI access token lives only in this page's memory and travels to the
 * same-origin relay in request headers, never in URLs.
 */
(function () {
  'use strict';

  var cfg = JSON.parse(document.getElementById('bridge-config').textContent);
  var frame = document.getElementById('frame');
  var statusEl = document.getElementById('status');
  var nameEl = document.getElementById('name');
  var roEl = document.getElementById('ro');

  var state = {
    version: cfg.version,
    dirty: false,
    dirtyRevision: 0,
    saving: false,
    lockId: null,
    opened: false
  };

  nameEl.textContent = cfg.name;
  document.title = cfg.name;
  if (!cfg.userCanWrite) roEl.hidden = false;

  function status(text, kind) {
    statusEl.textContent = text;
    statusEl.dataset.kind = kind || 'info';
  }

  function relay(op, headers, body) {
    var h = {
      'X-Bridge-Request': '1',
      'X-Wopi-Token': cfg.token,
      'X-Wopi-Src': cfg.src
    };
    Object.keys(headers || {}).forEach(function (k) { h[k] = headers[k]; });
    return fetch('/relay/' + op, {
      method: 'POST',
      headers: h,
      body: body === undefined ? null : body,
      credentials: 'omit',
      cache: 'no-store',
      keepalive: op === 'lock'
    });
  }

  function post(type, payload, transfer) {
    var msg = { type: cfg.app + ':' + type };
    Object.keys(payload || {}).forEach(function (k) { msg[k] = payload[k]; });
    frame.contentWindow.postMessage(msg, location.origin, transfer || []);
  }

  // ---- locking (advisory; Seahub stores it, Pro also sets the Seafile file lock)
  function takeLock() {
    if (!cfg.userCanWrite) return;
    state.lockId = 'bridge-' + Math.random().toString(36).slice(2) + Date.now().toString(36);
    relay('lock', { 'X-WOPI-Override': 'LOCK', 'X-WOPI-Lock': state.lockId }).then(function (r) {
      if (r.status === 409) {
        status('file is locked by another editor; saving may conflict', 'warn');
      }
    }).catch(function () { /* locks are best-effort */ });
    setInterval(function () {
      if (state.lockId) relay('lock', { 'X-WOPI-Override': 'REFRESH_LOCK', 'X-WOPI-Lock': state.lockId }).catch(function () {});
    }, Math.max(60, cfg.lockRefreshSeconds) * 1000);
  }

  function releaseLock() {
    if (!state.lockId) return;
    relay('lock', { 'X-WOPI-Override': 'UNLOCK', 'X-WOPI-Lock': state.lockId }).catch(function () {});
    state.lockId = null;
  }

  // ---- open
  function openDocument() {
    status('loading document…');
    relay('file').then(function (r) {
      if (!r.ok) return r.json().then(function (j) { throw new Error(j.error || ('HTTP ' + r.status)); });
      state.version = r.headers.get('X-Wopi-Version') || state.version;
      return r.arrayBuffer();
    }).then(function (buf) {
      if (buf.byteLength > cfg.maxBytes) throw new Error('document too large');
      post('open', { name: cfg.name, bytes: buf }, [buf]);
      state.opened = true;
      status(cfg.userCanWrite ? 'ready' : 'read-only', 'ok');
    }).catch(function (e) {
      status('cannot load: ' + e.message, 'error');
    });
  }

  // ---- save
  function handleSave(d) {
    var ticket = typeof d.ticket === 'string' ? d.ticket : null;
    function reject(err) {
      status(err, 'error');
      if (ticket) post('saveResult', { ticket: ticket, ok: false, error: err });
    }
    if (!cfg.userCanWrite) return reject('read-only: Seafile does not allow you to write this file');
    if (state.saving) return reject('a save is already in progress');
    if (d.saveAs || (d.name && d.name !== cfg.name)) return reject('Save As is not supported here; save keeps the file name');
    var bytes = d.bytes;
    if (bytes instanceof ArrayBuffer) bytes = new Uint8Array(bytes);
    if (!(bytes instanceof Uint8Array) || bytes.byteLength === 0) return reject('editor sent no document bytes');
    if (bytes.byteLength > cfg.maxBytes) return reject('document too large');

    var revision = state.dirtyRevision;
    state.saving = true;
    status('saving…');
    relay('save', {
      'Content-Type': 'application/octet-stream',
      'X-Expected-Version': state.version || '',
      'X-File-Name': encodeURIComponent(cfg.name)
    }, bytes).then(function (r) {
      return r.json().then(function (j) { return { status: r.status, body: j }; });
    }).then(function (res) {
      state.saving = false;
      if (res.status === 200) {
        state.version = res.body.version;
        if (state.dirtyRevision === revision) state.dirty = false;
        status(res.body.reconciled ? 'saved (reconciled after a lost response)' : 'saved to Seafile', 'ok');
        if (ticket) post('saveResult', { ticket: ticket, ok: true, version: res.body.version });
        return;
      }
      if (res.status === 409) {
        return reject('conflict: the file changed in Seafile since you opened it. Reopen it to see the current version; your edits stay in the editor.');
      }
      if (res.status === 401) return reject('your Seafile session for this file expired; reopen the file from Seafile');
      reject(res.body.error || ('save failed: HTTP ' + res.status));
    }).catch(function (e) {
      state.saving = false;
      reject('save failed: ' + e.message);
    });
  }

  // ---- editor messages
  window.addEventListener('message', function (e) {
    if (e.origin !== location.origin) return;
    if (e.source !== frame.contentWindow) return;
    var d = e.data;
    if (!d || typeof d.type !== 'string') return;
    var prefix = cfg.app + ':';
    if (d.type.indexOf(prefix) !== 0) return;
    var kind = d.type.slice(prefix.length);
    if (kind === 'ready') {
      if (!state.opened) openDocument();
    } else if (kind === 'openRequest') {
      openDocument();
    } else if (kind === 'dirty') {
      state.dirty = !!d.dirty;
      state.dirtyRevision++;
      if (state.dirty && !state.saving) status('unsaved changes', 'warn');
    } else if (kind === 'save') {
      handleSave(d);
    } else if (kind === 'failed') {
      status('editor error: ' + (d.error || 'unknown'), 'error');
    }
  });

  window.addEventListener('beforeunload', function (e) {
    if (state.dirty || state.saving) { e.preventDefault(); e.returnValue = ''; }
  });
  window.addEventListener('pagehide', releaseLock);

  takeLock();
  frame.src = cfg.editorUrl;
})();
