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
  window.addEventListener('keydown', function (e) {
    if (!ready || !openedName) return;
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && !e.altKey && (e.key === 's' || e.key === 'S')) {
      e.preventDefault(); e.stopPropagation();
      saveInPlace();
    }
  }, true);
  var saving = false;
  function saveInPlace() {
    if (saving || typeof api.execute !== 'function') return;
    saving = true;
    api.execute('file.save', { path: openedName }).then(function (r) {
      if (r && r.pending) return api.request('ui.dialog.confirm', {});   // e.g. SVG Options: accept defaults
    }).catch(function (err) {
      post('failed', { error: 'save: ' + (err && err.message || err) });
    }).then(function () { saving = false; pollSaves(); });
  }
  if (window.__craftHostShim === undefined) window.__craftHostShim = { save: saveInPlace };

  // Captured saves: the app keeps them in the page; forward each new or changed file to the host.
  var seen = {};
  function pollSaves() {
    if (!ready) return;
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
      if (post('save', { name: name, saveAs: saveAs, bytes: buf }, [buf]) && !saveAs) { lastHash = h; setDirty(false); }
    }
  }

  function setDirty(v) {
    if (dirtyReported === v) return;
    if (post('dirty', { dirty: v })) dirtyReported = v;
  }

  // Dirty state, when the app's inspect result carries one (key names differ per app).
  function pollDirty() {
    if (!ready || typeof api.request !== 'function') return;
    api.request('document.inspect', { depth: 0 }).then(function (r) {
      var v = findFlag(r, ['modified', 'dirty', 'unsaved', 'unsavedChanges'], 0);
      if (typeof v === 'boolean') setDirty(v);
    }, function () {});
  }
  function findFlag(o, keys, depth) {
    if (!o || typeof o !== 'object' || depth > 2) return undefined;
    for (var i = 0; i < keys.length; i++) if (typeof o[keys[i]] === 'boolean') return o[keys[i]];
    for (var k in o) { var v = findFlag(o[k], keys, depth + 1); if (typeof v === 'boolean') return v; }
    return undefined;
  }
})();
