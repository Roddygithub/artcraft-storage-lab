/* Lab host-protocol shim for Craft apps that have no `?host=parent` bridge upstream yet
 * but expose a page control API (`window.<app>`: openFile / readFile / files / execute / request).
 * It speaks the standard host message vocabulary so bridge/static/host.js needs no special case:
 *   -> `<app>:ready {version}`, `<app>:save {name, saveAs, bytes}`, `<app>:dirty {dirty}`, `<app>:failed {error}`
 *   <- `<app>:open {name, bytes}`
 *
 * Same-origin parent only; the source window is checked on every message.
 * This file is a lab adapter, not the app's code: the bundle itself is the upstream release,
 * with one <script> line added to index.html (`<script src="/host-shim.js" data-app="vectorcraft">`).
 * The proper fix is an upstream host.rs (kept locally as a proposal, unpublished).
 */
(function () {
  'use strict';

  var script = document.currentScript;
  var app = (script && script.dataset.app) || '';
  var isFigcraft = script && script.dataset.figcraft === 'true';
  var params = new URLSearchParams(location.search);
  if (!app || params.get('host') !== 'parent') return;

  var parent = window.parent;
  if (!parent || parent === window) return;
  var origin = location.origin;
  if (origin === 'null') return;
  try { if (parent.location.origin !== origin) return; } catch (e) { return; }

  // --- state ---
  var api = null;
  var openedName = null;
  var lastBytes = null;       // bytes of last successful host ACK
  var localBytes = null;      // bytes of current editor state
  var ready = false;
  var saveInFlight = null;    // { ticket, bytes, saveAs, timer }
  var queuedBytes = null;     // newer bytes waiting for ACK
  var nextTicket = 0;
  var inspectSerial = 0;
  var dirtyReported = false;

  // --- helpers ---
  function post(type, payload, transfer) {
    var m = { type: app + ':' + type };
    if (payload) for (var k in payload) m[k] = payload[k];
    try { parent.postMessage(m, origin, transfer || []); return true; } catch (e) { return false; }
  }
  function sameBytes(a, b) {
    if (!a || !b || a.length !== b.length) return false;
    for (var i = 0; i < a.length; i++) if (a[i] !== b[i]) return false;
    return true;
  }
  function fileName(p) { return String(p).split(/[\\/]/).pop() || String(p); }
  function reportDirty(v, force) {
    // Only report clean after reconciling any pending local captures.
    if (!v) {
      if (saveInFlight || !sameBytes(localBytes, lastBytes)) return;
    }
    if (dirtyReported === v && !force) return;
    if (post('dirty', { dirty: v })) dirtyReported = v;
  }

  // --- wait for app API ---
  var started = Date.now();
  (function waitForApp() {
    api = window[app];
    if (api && typeof api.commands === 'function') {
      api.commands().then(function () {
        ready = true;
        try { api.captureDownloads(true); } catch (e) {}
        post('ready', { version: 'page-api-shim' });
        setInterval(pollSaves, 500);
        setInterval(pollDirty, 1000);
      }, function () { setTimeout(waitForApp, 250); });
      return;
    }
    if (Date.now() - started > 120000) { post('failed', { error: app + ' page API never appeared' }); return; }
    setTimeout(waitForApp, 250);
  })();

  // --- parent message handler ---
  window.addEventListener('message', function (e) {
    if (e.origin !== origin || e.source !== parent) return;
    var d = e.data || {};
    var prefix = app + ':';

    // saveResult from host (ACK after PutFile)
    if (d.type === prefix + 'saveResult') {
      if (!saveInFlight || d.ticket !== saveInFlight.ticket) return;
      clearTimeout(saveInFlight.timer);
      var ok = (d.ok === true);
      var saved = saveInFlight;
      saveInFlight = null;

      if (ok) {
        lastBytes = saved.bytes;
        // If there are queued bytes, send them now
        if (queuedBytes) {
          var buf = queuedBytes.buffer.slice(queuedBytes.byteOffset, queuedBytes.byteOffset + queuedBytes.byteLength);
          var ticket = app + ':shim:' + (++nextTicket);
          saveInFlight = { ticket: ticket, bytes: queuedBytes, timer: null };
          reportDirty(true);
          queuedBytes = null;
          if (!post('save', { name: openedName, saveAs: false, bytes: buf, ticket: ticket }, [buf])) {
            saveInFlight = null;
            post('failed', { error: 'could not send save to host; retry Save' });
          } else {
            saveInFlight.timer = setTimeout(function () {
              if (!saveInFlight || saveInFlight.ticket !== ticket) return;
              saveInFlight = null;
              reportDirty(true);
              post('failed', { error: 'host save confirmation timed out; retry Save' });
            }, 120000);
          }
        } else {
          pollSaves();
        }
      } else {
        // Host rejected; keep dirty so user can retry.
        reportDirty(true);
      }
      return;
    }

    // open from host
    if (d.type !== prefix + 'open') return;
    var bytes = d.bytes instanceof ArrayBuffer ? new Uint8Array(d.bytes) : d.bytes;
    if (!(bytes instanceof Uint8Array)) return;
    openedName = (d.name && String(d.name).trim()) || ('document.' + app);
    lastBytes = bytes.slice();
    localBytes = bytes.slice();
    (function tryOpen(n) {
      var ok = false;
      try { ok = api && api.openFile(openedName, bytes); } catch (err) { ok = false; }
      if (!ok && n < 40) setTimeout(function () { tryOpen(n + 1); }, 250);
    })(0);
  });

  // --- Ctrl+S handler ---
  window.addEventListener('keydown', function (e) {
    if (!ready || !openedName) return;
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && !e.altKey && (e.key === 's' || e.key === 'S')) {
      e.preventDefault(); e.stopPropagation();
      // Always allow local save to execute (updates capture/localBytes).
      // Host send is gated by saveInFlight; pollSaves queues behind ACK.
      saveInPlace();
    }
  }, true);

  // --- save flow ---
  var saving = false;
  function saveInPlace() {
    if (saving || typeof api.execute !== 'function') return;
    // Allow local save to execute (updates capture) even when host save in flight.
    // Host send is gated by saveInFlight; pollSaves will queue behind ACK.
    saving = true;
    saveInPlaceImpl().catch(function (err) {
      post('failed', { error: 'save: ' + (err && err.message || err) });
    }).then(function () { saving = false; pollSaves(); });
  }

  async function saveInPlaceImpl() {
    // FigCraft web refuses `file.save {path}` ("no file system in the browser").
    // Its Save shortcut triggers a download, which captureDownloads captures.
    // We replay the shortcut via the control channel.
    if (isFigcraft) {
      await api.request('ui.key', { key: 's', cmd: true });
      await new Promise(function (res) { setTimeout(res, 600); });
      await api.request('ui.dialog.confirm', {}).catch(function () {});
      pollSaves(); // check for captured download
      return;
    }

    // VectorCraft and others: save with explicit path.
    await api.execute('file.save', { path: openedName }).catch(function (err) {
      // Fallback: if path save fails, try generic save (may open dialog).
      return api.execute('file.save', {});
    });
    // Accept common dialogs (e.g., SVG options).
    await api.request('ui.dialog.confirm', {}).catch(function () {});
    pollSaves(); // check for captured file after save
  }

  // --- poll for editor captures ---
  function pollSaves() {
    if (!ready) return;
    var list;
    try { list = api.files() || []; } catch (e) { return; }
    for (var i = 0; i < list.length; i++) {
      var name = fileName(list[i].path);
      var bytes;
      try { bytes = api.readFile(name); } catch (e) { continue; }
      if (!(bytes instanceof Uint8Array)) continue;

      localBytes = bytes.slice();

      // Already acknowledged exact bytes
      if (sameBytes(bytes, lastBytes)) continue;

      // Save already in flight to host - queue this version
      if (saveInFlight) {
        if (name === openedName && !sameBytes(bytes, saveInFlight.bytes)) {
          // Queue newer bytes to send after current ACK
          queuedBytes = bytes.slice();
          reportDirty(true);
        }
        continue;
      }

      // New or changed file - send to host
      var saveAs = openedName !== null && name !== openedName;
      var buf = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
      if (saveAs) {
        post('save', { name: name, saveAs: true, bytes: buf }, [buf]);
        continue;
      }

      // In-place save: send with ticket
      var ticket = app + ':shim:' + (++nextTicket);
      saveInFlight = { ticket: ticket, bytes: bytes.slice(), timer: null };
      reportDirty(true);
      if (!post('save', { name: name, saveAs: false, bytes: buf, ticket: ticket }, [buf])) {
        saveInFlight = null;
        post('failed', { error: 'could not send save to host; retry Save' });
        return;
      }
      saveInFlight.timer = setTimeout(function () {
        if (!saveInFlight || saveInFlight.ticket !== ticket) return;
        saveInFlight = null;
        reportDirty(true);
        post('failed', { error: 'host save confirmation timed out; retry Save' });
      }, 120000);
      return; // one save at a time
    }
  }

  // --- poll dirty state from app ---
  function pollDirty() {
    if (!ready || typeof api.request !== 'function') return;
    var serial = ++inspectSerial;
    api.request('document.inspect', { depth: 0 }).then(function (r) {
      if (serial !== inspectSerial) return;
      var v = findFlag(r, ['modified', 'dirty', 'unsaved', 'unsavedChanges'], 0);
      if (typeof v === 'boolean' && (v || !saveInFlight)) reportDirty(v, v);
    }, function () {});
  }
  function findFlag(o, keys, depth) {
    if (!o || typeof o !== 'object' || depth > 2) return undefined;
    for (var i = 0; i < keys.length; i++) if (typeof o[keys[i]] === 'boolean') return o[keys[i]];
    for (var k in o) { var v = findFlag(o[k], keys, depth + 1); if (typeof v === 'boolean') return v; }
    return undefined;
  }
})();