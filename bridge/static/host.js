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
    opened: false,
    failedSave: false,
    savedStatus: null,
    lastBytes: null
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

  // A browser download from the host page (outside the editor's sandbox).
  function downloadBytes(name, bytes) {
    try {
      var safe = name.replace(/[\\/:*?"<>|\u0000-\u001f]/g, '_').slice(0, 255) || 'export';
      var url = URL.createObjectURL(new Blob([bytes], { type: 'application/octet-stream' }));
      var a = document.createElement('a');
      a.href = url; a.download = safe; a.style.display = 'none';
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 10000);
      return true;
    } catch (e) { return false; }
  }

  // ---- token lifetime (Seahub posts access_token_ttl = expiry, ms since the epoch)
  function tokenExpired() { return cfg.tokenTtl > 0 && Date.now() >= cfg.tokenTtl; }
  if (cfg.tokenTtl > 0) {
    var warnAt = cfg.tokenTtl - 5 * 60 * 1000;
    setTimeout(function () {
      if (!tokenExpired()) status('your Seafile session for this file ends in 5 minutes; save now, then reopen the file', 'warn');
    }, Math.max(0, warnAt - Date.now()));
    setTimeout(function () {
      status(state.dirty ? 'session expired: the next save downloads your document instead of writing to Seafile' : 'session expired; reopen the file from Seafile to keep editing', state.dirty ? 'error' : 'warn');
    }, Math.max(0, cfg.tokenTtl - Date.now()));
  }
  window.addEventListener('pageshow', function (e) { if (e.persisted && cfg.userCanWrite && !state.lockId) takeLock(); });

  // ---- save
  function handleSave(d) {
    var ticket = typeof d.ticket === 'string' ? d.ticket : null;
    function reject(err) {
      // A refused save means the editor's content is NOT in Seafile: the page stays dirty (unload
      // guard) whatever the editor believes, until a later save succeeds.
      state.dirty = true; state.dirtyRevision++; state.failedSave = true;
      status(err, 'error');
      if (ticket) post('saveResult', { ticket: ticket, ok: false, error: err });
    }
    var bytes = d.bytes;
    if (bytes instanceof ArrayBuffer) bytes = new Uint8Array(bytes);
    if (!(bytes instanceof Uint8Array) || bytes.byteLength === 0) return reject('editor sent no document bytes');
    if (d.saveAs || (d.name && d.name !== cfg.name)) {
      // Save As / Export: the Seafile file keeps its name and content; the user gets the bytes as a
      // browser download instead (the editor would have downloaded them without a host anyway).
      // Not acknowledged as stored: the document in Seafile is unchanged.
      var exported = downloadBytes(String(d.name || ('export-' + cfg.name)), bytes);
      status(exported ? 'exported ' + d.name + ' as a download; the Seafile file is unchanged' : 'export could not be downloaded', exported ? 'warn' : 'error');
      if (ticket) post('saveResult', { ticket: ticket, ok: false, error: exported ? 'exported as a download, not saved to Seafile' : 'export failed' });
      return;
    }
    if (!cfg.userCanWrite) return reject('read-only: Seafile does not allow you to write this file');
    if (state.saving) return reject('a save is already in progress');
    if (bytes.byteLength > cfg.maxBytes) return reject('document too large');

    if (tokenExpired()) {
      downloadBytes(cfg.name, bytes);
      return reject('your Seafile session for this file expired; your document was downloaded instead. Reopen the file from Seafile and open the download');
    }
    var revision = state.dirtyRevision;
    state.lastBytes = bytes;
    state.saving = true;
    status('saving…');
    relay('save', {
      'Content-Type': 'application/octet-stream',
      'X-Expected-Version': state.version || '',
      'X-File-Name': encodeURIComponent(cfg.name)
    }, bytes).then(function (r) {
      // A proxy may answer with HTML (504 page): never let a non-JSON body look like a crash.
      return r.text().then(function (t) { var j; try { j = JSON.parse(t); } catch (e) { j = { error: 'HTTP ' + r.status + ' from the proxy' }; } return { status: r.status, body: j }; });
    }).then(function (res) {
      state.saving = false;
      if (res.status === 200 && res.body && res.body.verified === true &&
          typeof res.body.version === 'string' && res.body.version.trim()) {
        state.version = res.body.version;
        state.savedStatus = res.body.reconciled ? 'saved (reconciled after a lost response)' : 'saved to Seafile';
        if (state.dirtyRevision === revision) {
          state.failedSave = false;
          state.dirty = false;
        }
        if (state.failedSave) status('earlier save verified; newer save failed, save again before closing', 'error');
        else if (state.dirty) status('saved earlier edits to Seafile; unsaved changes remain', 'warn');
        else status(state.savedStatus, 'ok');
        if (ticket) post('saveResult', { ticket: ticket, ok: true, version: res.body.version });
        return;
      }
      if (res.status === 200) return reject('save failed: the bridge did not verify the stored document');
      if (res.status === 409) {
        return reject('conflict: the file changed in Seafile since you opened it. Reopen it to see the current version; your edits stay in the editor.');
      }
      if (res.status === 401) {
        downloadBytes(cfg.name, bytes);
        return reject('your Seafile session for this file expired; your document was downloaded instead. Reopen the file from Seafile and open the download');
      }
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
      // Only new edits advance the save snapshot. A clean notification is not
      // storage verification and must not resolve a pending or failed save.
      if (d.dirty) {
        state.dirty = true;
        state.dirtyRevision++;
      } else if (!state.failedSave && !state.saving) {
        var wasDirty = state.dirty;
        state.dirty = false;
        if (wasDirty && state.savedStatus && !tokenExpired()) status(state.savedStatus, 'ok');
      }
      if (state.dirty && !state.saving && !state.failedSave) status('unsaved changes', 'warn');
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
