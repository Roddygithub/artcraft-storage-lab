"""The host page: the parent side of the Craft `?host=parent` bridge.

This page is what Seafile's third-party-editor hook loads (through a form POST
inside an iframe). It embeds the Craft web app in a same-origin iframe and
implements the host half of the protocol described in docs/HOST-CONTRACT.md:

    child -> host   <app>:ready  { version }
    host  -> child  <app>:open   { name, bytes }
    child -> host   <app>:save   { name, bytes }
    child -> host   <app>:dirty  { dirty }
    child -> host   <app>:failed { error }

The browser never holds a Seafile credential. The only thing it holds is the
session id, which the server maps to one document for one user.
"""

import html
import json

_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  html, body { margin:0; padding:0; height:100%; background:#f5f5f5;
                font: 13px/1.5 system-ui, sans-serif; color:#222; }
  #frame { position:absolute; inset:0 0 34px 0; width:100%; height:calc(100% - 34px);
           border:0; display:block; }
  #bar  { position:absolute; left:0; right:0; bottom:0; height:34px; display:flex;
          align-items:center; gap:12px; padding:0 12px; background:#fff;
          border-top:1px solid #ddd; box-sizing:border-box; }
  #state { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .ok { color:#137333; } .err { color:#c5221f; } .busy { color:#5f6368; }
  a { color:#1a73e8; }
</style>
</head>
<body>
<iframe id="frame" src="__APP_URL__" allow="fullscreen; clipboard-read; clipboard-write"></iframe>
<div id="bar">
  <span id="state" class="busy">Connecting to __APP_NAME__&hellip;</span>
  <span id="meta"></span>
</div>
<script>
"use strict";
const SID = __SID__;
const APP = __APP__;          // "wordcraft"
const CAN_EDIT = __CAN_EDIT__;
const FILE_NAME = __FILE_NAME__;
const frame = document.getElementById("frame");
const state = document.getElementById("state");

function say(text, cls) {
  state.textContent = text;
  state.className = cls || "busy";
}

// The Craft app is served from this origin, so the origin we talk to is our own.
const ORIGIN = location.origin;

function toCraft(type, extra) {
  const msg = Object.assign({ type: APP + ":" + type }, extra || {});
  frame.contentWindow.postMessage(msg, ORIGIN);
}

// ---------------------------------------------------------------------------
// VectorCraft's transport.
//
// VectorCraft does not speak the `?host=parent` protocol: it exposes its own
// page API (`window.vectorcraft`), which is the same control protocol the
// desktop app and the CLI speak. It is deterministic -- `openFile`,
// `execute`, `captureDownloads`, `files`, `readFile` -- and it is how a
// non-Office format is proved round.
//
// There is no dirty signal and no save event on that API, so the host page
// polls the saved files instead.
// ---------------------------------------------------------------------------
const VECTORCRAFT = (APP === "vectorcraft");
let lastSavedHash = null;      // the content we last stored, not its size
let saving = false;

// The frame we are about to drive must be the one we created, on our own
// origin. A direct property read crosses no boundary that postMessage would
// have checked, so the check is made here instead.
function frameIsOurs() {
  try {
    return frame.contentWindow && frame.contentWindow.location.origin === ORIGIN;
  } catch (err) {
    return false;                 // reading a cross-origin location throws
  }
}

function waitForApi() {
  return new Promise((resolve, reject) => {
    let tries = 0;
    const tick = () => {
      if (!frameIsOurs()) { if (++tries > 200) return reject(new Error("the editor's frame is not ours")); return setTimeout(tick, 250); }
      const f = frame.contentWindow;
      if (f && f.vectorcraft && typeof f.vectorcraft.openFile === "function") return resolve(f.vectorcraft);
      if (++tries > 200) return reject(new Error("the editor's page API did not appear"));
      setTimeout(tick, 250);
    };
    tick();
  });
}

// A cheap content fingerprint. VectorCraft's page API has no save event and no
// dirty signal, so the only way to notice a save that produced the same bytes as
// the last one is to look at the bytes themselves.
function fingerprint(bytes) {
  let h = 2166136261 >>> 0;
  const view = new Uint8Array(bytes);
  for (let i = 0; i < view.length; i++) {
    h ^= view[i];
    h = Math.imul(h, 16777619) >>> 0;
  }
  return view.length + ":" + h.toString(16);
}

async function openThroughApi(api) {
  say("Loading " + FILE_NAME + "…");
  const resp = await fetch("/session/" + SID + "/document", { credentials: "same-origin" });
  if (!resp.ok) throw new Error("HTTP " + resp.status);
  const buf = await resp.arrayBuffer();
  api.captureDownloads(true);
  if (!api.openFile(FILE_NAME, new Uint8Array(buf))) throw new Error("the editor refused the file");
  say(FILE_NAME + " opened", "ok");
}

function pollSaved(api) {
  setInterval(async () => {
    if (saving) return;
    let files;
    try { files = await api.files(); } catch (e) { return; }
    if (!Array.isArray(files)) return;
    const mine = files.find((f) => (f.path || "").endsWith(FILE_NAME));
    if (!mine || !mine.size) return;
    saving = true;
    let bytes;
    try {
      bytes = await api.readFile(FILE_NAME);
    } catch (err) {
      saving = false;
      return;
    }
    const hash = fingerprint(bytes);
    if (hash === lastSavedHash) { saving = false; return; }
    try {
      say("Saving…", "busy");
      const resp = await fetch("/session/" + SID + "/save", {
        method: "POST", credentials: "same-origin",
        headers: { "Content-Type": "application/octet-stream" }, body: bytes,
      });
      const result = await resp.json();
      window.__lastSave = result;
      const ok = !!resp.ok && result.ok === true;
      // Only a stored save becomes the new baseline: a refused one is retried on
      // the next poll, which is what makes a failed save visible instead of lost.
      if (ok) lastSavedHash = hash;
      const version = ok ? (result.version ? " — new version " + result.version : "") : "";
      say(ok ? ("Saved" + version) : ("Save failed: " + (result.error || resp.status)),
          ok ? "ok" : "err");
    } catch (err) {
      say("Save failed: " + err.message, "err");
    } finally {
      saving = false;
    }
  }, 700);
}

// VectorCraft's page API has no dirty signal, so the host page cannot warn about
// unsaved *edits*. It can warn while a save is on its way to the server, which is
// the window in which closing the tab would lose bytes the editor already handed
// over. (The editor itself keeps unsaved work in recovery copies in the browser.)
window.addEventListener("beforeunload", (event) => {
  if (saving) {
    event.preventDefault();
    event.returnValue = "";
  }
});

if (VECTORCRAFT) {
  waitForApi().then(async (api) => {
    await openThroughApi(api);
    pollSaved(api);
  }).catch((err) => say("Could not start: " + err.message, "err"));
}

// The message listener belongs to the WINDOW: a message posted by the child
// frame is delivered to the parent's window, not to the <iframe> element.
window.addEventListener("message", async (event) => {
  // Both checks: the origin AND the source window. A page on our origin that is
  // not our frame must not be able to inject bytes or claim a save.
  if (event.origin !== ORIGIN) return;
  if (event.source !== frame.contentWindow) return;
  const data = event.data;
  if (!data || typeof data !== "object") return;

  switch (data.type) {
    case APP + ":ready":
      if (VECTORCRAFT) break;           // VectorCraft is driven by its own API above
      say("Loading " + FILE_NAME + "…");
      try {
        const resp = await fetch("/session/" + SID + "/document", { credentials: "same-origin" });
        if (!resp.ok) throw new Error("HTTP " + resp.status);
        const buf = await resp.arrayBuffer();
        toCraft("open", { name: FILE_NAME, bytes: new Uint8Array(buf) });
        say(FILE_NAME + " opened", "ok");
      } catch (err) {
        say("Could not load the document: " + err.message, "err");
      }
      break;

    case APP + ":save": {
      const bytes = data.bytes instanceof ArrayBuffer ? new Uint8Array(data.bytes) : data.bytes;
      // The ticket the app gave this save, if it uses one (WordCraft's async_saves).
      const ticket = data.ticket;
      say("Saving…", "busy");
      let ok = false;
      let error = "the save did not happen";
      try {
        const resp = await fetch("/session/" + SID + "/save", {
          method: "POST",
          credentials: "same-origin",
          headers: { "Content-Type": "application/octet-stream" },
          body: bytes,
        });
        const result = await resp.json();
        ok = !!resp.ok && result.ok === true;
        if (!ok) {
          error = result.error || ("HTTP " + resp.status);
        } else {
          error = "";
        }
        window.__lastSave = result;
        say(ok ? ("Saved" + (result.version ? " — new version " + result.version : "")) : ("Save failed: " + error),
            ok ? "ok" : "err");
      } catch (err) {
        error = err.message;
        say("Save failed: " + error, "err");
      }
      // Tell the app how the save ended. Without this the app waits for a
      // confirmation that never comes and the document stays dirty forever.
      if (ticket !== undefined && ticket !== null) {
        // The app shows this message to the user, so it must not carry the
        // internals (paths, ids, upstream answers). The full error stays in the
        // host page's console and in the service's log.
        const shown = ok ? "" : "the file could not be stored";
        toCraft("saveResult", { ticket: ticket, ok: ok, error: shown });
      }
      break;
    }

    case APP + ":dirty":
      window.__lastDirty = !!data.dirty;
      // The gateway keeps the "not persisted" state, so the host can warn on
      // close and the service knows the document is unsaved.
      fetch("/session/" + SID + "/dirty", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "text/plain" },
        body: data.dirty ? "true" : "false",
      }).catch(() => {});
      say(data.dirty ? "Unsaved changes" : FILE_NAME + " (no changes)", data.dirty ? "busy" : "ok");
      break;

    case APP + ":failed":
      say("The editor could not start: " + (data.error || "unknown error"), "err");
      break;
  }
});

// The Craft app asks for a document by opening it; in host mode the host
// decides what is opened, so we answer the request ourselves.
frame.addEventListener("load", () => { /* nothing: :ready drives the flow */ });

if (!CAN_EDIT) {
  document.getElementById("meta").innerHTML = "<em>read-only</em>";
}
</script>
</body>
</html>
"""


def render(sid, app, app_url, file_name, can_edit):
    """Render the host page for one editing session."""
    return (
        _TEMPLATE
        .replace("__TITLE__", html.escape(file_name))
        .replace("__APP_URL__", html.escape(app_url, quote=True))
        .replace("__APP_NAME__", html.escape(app))
        .replace("__SID__", json.dumps(sid))
        .replace("__APP__", json.dumps(app))
        .replace("__CAN_EDIT__", "true" if can_edit else "false")
        .replace("__FILE_NAME__", json.dumps(file_name))
    )
