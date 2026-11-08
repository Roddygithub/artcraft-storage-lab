/* Lab host-protocol shim for Craft apps that have no `?host=parent` bridge upstream yet but expose
 * the page control API (`window.<app>`: openFile / captureDownloads / files / readFile / request).
 * It speaks exactly the message vocabulary of the upstream bridges (WordCraft/GridCraft/PdfCraft/
 * CADCraft host.rs) so bridge/static/host.js needs no special case:
 *   -> `<app>:ready {version}`, `<app>:save {name, saveAs, bytes}`, `<app>:dirty {dirty}`, `<app>:failed {error}`
 *   <- `<app>:open {name, bytes}`
 * Same-origin parent only; the source window is checked on every message. This file is a lab
 * adapter, not the app's code: the bundle itself is the upstream release, with one <script> line
 * added to index.html. The proper fix is an upstream host.rs (kept locally as a proposal, unpublished).
 */
(function () {
  'use strict';
  var script = document.currentScript;
  var app = (script && script.dataset.app) || '';
  var params = new URLSearchParams(location.search);
  if (!app || params.get('host') !== 'parent') return;
  var parent = window.parent;
  if (!parent || parent === window) return;
  var origin = location.origin;
  if (origin === 'null') return;
  try { if (parent.location.origin !== origin) return; } catch (e) { return; }

  var api = null, openedName = null, lastHash = null, ready = false, dirtyReported = null;
  var pending = null, nextTicket = 0, saveFailed = false, lastAck = null;
  var inspectSerial = 0;

  function post(type, payload, transfer) {
    var m = { type: app + ':' + type };
    if (payload) for (var k in payload) m[k] = payload[k];
    try { parent.postMessage(m, origin, transfer || []); return true; } catch (e) { return false; }
  }

  function fnv(bytes) { // cheap content fingerprint
    var h = 0x811c9dc5;
    for (var i = 0; i < bytes.length; i++) { h ^= bytes[i]; h = Math.imul(h, 0x01000193) >>> 0; }
    return bytes.length + ':' + h;
  }

  function fileName(p) { return String(p).split(/[\\/]/).pop() || String(p); }

  // The app announces itself once its control channel answers.
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

  window.addEventListener('message', function (e) {
    if (e.origin !== origin || e.source !== parent) return;
    var d = e.data || {};
    if (d.type === app + ':saveResult') {
      if (!pending || d.ticket !== pending.ticket) return;
      clearTimeout(pending.timer);
      var saved = pending;
      pending = null;
      if (d.ok === true) {
        lastHash = saved.hash;
        saveFailed = false;
        lastAck = d.ticket;
        // The ACK verifies the captured bytes, not edits made after serialization.
        // Keep the guard until the current editor state itself reports clean.
        if (typeof api.request === 'function') {
          var serial = ++inspectSerial;
          api.request('document.inspect', { depth: 0 }).then(function (result) {
            if (serial !== inspectSerial || pending || lastAck !== d.ticket) return;
            var dirty = findFlag(result, ['modified', 'dirty', 'unsaved', 'unsavedChanges'], 0);
            setDirty(dirty !== false, dirty !== false);
          }, function () {
            if (serial === inspectSerial && !pending && lastAck === d.ticket) setDirty(true, true);
          });
        } else setDirty(true, true);
      } else {
        saveFailed = true;
        setDirty(true);
      }
      return;
    }
    if (d.type !== app + ':open') return;
    var bytes = d.bytes instanceof ArrayBuffer ? new Uint8Array(d.bytes) : d.bytes;
    if (!(bytes instanceof Uint8Array)) return;
    openedName = (d.name && String(d.name).trim()) || ('document.' + app);
    lastHash = fnv(bytes);           // what the host already has: a re-save of identical bytes is not a save
    (function tryOpen(n) {
      var ok = false;
      try { ok = api && api.openFile(openedName, bytes); } catch (err) { ok = false; }
      if (!ok && n < 40) setTimeout(function () { tryOpen(n + 1); }, 250);
    })(0);
  });

  // Save = write the opened file under its own name, as the desktop app does. The app's own Ctrl/Cmd+S
  // on a document that arrived as bytes opens a Save As panel (new name, native format), which the
  // host would refuse; so the shortcut is taken here and turned into `file.save {path}`.
  var pathSaveUnsupported = false;   // FigCraft web: "no file system in the browser" -- its own Save shortcut then runs
  window.addEventListener('keydown', function (e) {
    if (!ready || !openedName) return;
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && !e.altKey && (e.key === 's' || e.key === 'S')) {
      seen[openedName] = null; // An explicit retry may resend the same refused bytes.
      if (pathSaveUnsupported) return;
      e.preventDefault(); e.stopPropagation();
      saveInPlace();
    }
  }, true);
  var saving = false;
  function saveInPlace() {
    if (saving || typeof api.execute !== 'function') return;
    seen[openedName] = null;
    saving = true;
    // With a path the app writes the file directly (VectorCraft). An app whose web build refuses
    // paths ("no file system in the browser": FigCraft) saves through its download path instead,
    // which captureDownloads keeps under the opened name.
    api.execute('file.save', { path: openedName }).catch(function (err) {
      if (/no file system/i.test(String(err && err.message || err))) {
        // The app's own Save (download path, captured by captureDownloads) is the only way: replay
        // the shortcut through the control channel and accept the name/format dialog if one opens.
        pathSaveUnsupported = true;
        return api.request('ui.key', { key: 's', cmd: true }).then(function () {
          return new Promise(function (res) { setTimeout(res, 600); });
        }).then(function () { return api.request('ui.dialog.confirm', {}).catch(function () {}); });
      }
      return api.execute('file.save', {});
    }).then(function (r) {
      if (r && r.pending) return api.request('ui.dialog.confirm', {});   // e.g. SVG Options: accept defaults
    }).catch(function (err) {
      post('failed', { error: 'save: ' + (err && err.message || err) });
    }).then(function () { saving = false; pollSaves(); });
  }
  if (window.__craftHostShim === undefined) window.__craftHostShim = { save: saveInPlace };

  // Captured saves: the app keeps them in the page; forward each new or changed file to the host.
  var seen = {};
  function pollSaves() {
    if (!ready || pending) return;
    var list;
    try { list = api.files() || []; } catch (e) { return; }
    for (var i = 0; i < list.length; i++) {
      var name = fileName(list[i].path), size = list[i].size;
      var bytes;
      try { bytes = api.readFile(name); } catch (e) { continue; }
      if (!(bytes instanceof Uint8Array)) continue;
      var h = fnv(bytes);
      if (seen[name] === h) continue;
      seen[name] = h;
      if (name === openedName && h === lastHash) continue;   // nothing new
      var saveAs = openedName !== null && name !== openedName;
      var buf = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
      if (saveAs) {
        post('save', { name: name, saveAs: true, bytes: buf }, [buf]);
        continue;
      }
      var ticket = app + ':shim:' + (++nextTicket);
      pending = { ticket: ticket, hash: h, timer: null };
      setDirty(true);
      if (!post('save', { name: name, saveAs: false, bytes: buf, ticket: ticket }, [buf])) {
        pending = null;
        saveFailed = true;
        post('failed', { error: 'could not send save to host; retry Save' });
        return;
      }
      pending.timer = setTimeout(function () {
        if (!pending || pending.ticket !== ticket) return;
        pending = null;
        saveFailed = true;
        setDirty(true);
        post('failed', { error: 'host save confirmation timed out; retry Save' });
      }, 120000);
      return;
    }
  }

  function setDirty(v, force) {
    if (dirtyReported === v && !force) return;
    if (post('dirty', { dirty: v })) dirtyReported = v;
  }

  // Dirty state, when the app's inspect result carries one (key names differ per app).
  function pollDirty() {
    if (!ready || typeof api.request !== 'function') return;
    var serial = ++inspectSerial;
    api.request('document.inspect', { depth: 0 }).then(function (r) {
      if (serial !== inspectSerial) return;
      var v = findFlag(r, ['modified', 'dirty', 'unsaved', 'unsavedChanges'], 0);
      if (typeof v === 'boolean' && (v || (!pending && !saveFailed))) setDirty(v, v);
    }, function () {});
  }
  function findFlag(o, keys, depth) {
    if (!o || typeof o !== 'object' || depth > 2) return undefined;
    for (var i = 0; i < keys.length; i++) if (typeof o[keys[i]] === 'boolean') return o[keys[i]];
    for (var k in o) { var v = findFlag(o[k], keys, depth + 1); if (typeof v === 'boolean') return v; }
    return undefined;
  }
})();
