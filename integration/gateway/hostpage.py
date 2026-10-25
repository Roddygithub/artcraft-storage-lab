"""The host page: the parent side of the Craft `?host=parent` bridge.

This page is what Seafile's third-party-editor hook loads (through a form POST
inside an iframe). It embeds the Craft web app in a same-origin iframe and
implements the host half of the protocol described in docs/HOST-CONTRACT.md:

    child -> host   <app>:ready  { version }
    child -> host   <app>:openRequest { purpose }
    host  -> child  <app>:open   { name, bytes }
    child -> host   <app>:save   { ticket, name, bytes }
    host  -> child  <app>:saveResult { ticket, ok, error? }
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
<style nonce="__CSP_NONCE__">
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
<script nonce="__CSP_NONCE__">
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

function fileExtension(name) {
  const dot = typeof name === "string" ? name.lastIndexOf(".") : -1;
  return dot < 0 ? "" : name.slice(dot + 1).toLowerCase();
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
let lastSavedBytes = null;     // exact bytes from Seafile or the last committed save
let saving = false;
window.__lastDirty = false;
window.__editorConfirmedSave = false;
window.__saveConfirmationPending = false;
let dirtyRevision = 0;
let saveRevision = -1;

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

function copyBytes(bytes) {
  return new Uint8Array(bytes).slice();
}

function sameBytes(left, right) {
  if (!right) return false;
  const a = new Uint8Array(left);
  const b = new Uint8Array(right);
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) return false;
  return true;
}

async function openThroughApi(api) {
  say("Loading " + FILE_NAME + "…");
  const resp = await fetch("/session/" + SID + "/document", { credentials: "same-origin" });
  if (!resp.ok) throw new Error("HTTP " + resp.status);
  const buf = await resp.arrayBuffer();
  lastSavedBytes = copyBytes(buf);
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
    if (sameBytes(bytes, lastSavedBytes)) {
      // Equal output is a no-op, not evidence of an editor dirty/save event.
      saving = false;
      return;
    }
    window.__lastDirty = true;
    try {
      say("Saving…", "busy");
      window.__saveInFlight = true;
      const resp = await fetch("/session/" + SID + "/save", {
        method: "POST", credentials: "same-origin",
        headers: { "Content-Type": "application/octet-stream", "X-ArtCraft-Filename": FILE_NAME }, body: bytes,
      });
      const result = await resp.json();
      window.__lastSave = result;
      const ok = !!resp.ok && result.ok === true;
      // Only a stored save becomes the new baseline: a refused one is retried on
      // the next poll, which is what makes a failed save visible instead of lost.
      if (ok) {
        lastSavedBytes = copyBytes(bytes);
        try {
          const current = await api.readFile(FILE_NAME);
          window.__lastDirty = !sameBytes(current, lastSavedBytes);
        } catch (err) {
          window.__lastDirty = true;
        }
      } else {
        window.__lastDirty = true;
      }
      const version = ok ? (result.version ? " — new version " + result.version : "") : "";
      say(ok ? ("Saved" + version) : ("Save failed: " + (result.error || resp.status)),
          ok ? "ok" : "err");
    } catch (err) {
      window.__lastDirty = true;
      say("Save failed: " + err.message, "err");
    } finally {
      window.__saveInFlight = false;
      saving = false;
    }
  }, 700);
}

// Warn before unloading while an editor is dirty or its bytes are in flight.
// VectorCraft has no dirty signal, so only its save-in-flight window is visible.
window.addEventListener("beforeunload", (event) => {
  if (window.__lastDirty === true || window.__saveInFlight || saving) {
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

    case APP + ":openRequest":
      // This editing session is scoped to the single file selected in Seahub.
      // Do not silently reuse that file's capability to browse the library.
      if (data.purpose === "open") {
        say("To open another document, return to Seafile and select it.", "busy");
      }
      break;

    case APP + ":save": {
      const bytes = data.bytes instanceof ArrayBuffer ? new Uint8Array(data.bytes) : data.bytes;
      // The ticket the app gave this save, if it uses one (WordCraft's async_saves).
      const ticket = data.ticket;
      // This session is bound to exactly one Seafile document. Editors may
      // serialize their internal project title, which is not the storage name;
      // pin the write to the selected file and refuse Save As / exports.
      const requestedName = typeof data.name === "string" ? data.name : FILE_NAME;
      if (data.saveAs === true || fileExtension(requestedName) !== fileExtension(FILE_NAME)) {
        window.__lastDirty = true;
        window.__editorConfirmedSave = false;
        window.__saveConfirmationPending = false;
        fetch("/session/" + SID + "/dirty", {
          method: "POST", credentials: "same-origin",
          headers: { "Content-Type": "text/plain" }, body: "true",
        }).catch(() => {});
        if (ticket !== undefined && ticket !== null) {
          toCraft("saveResult", { ticket: ticket, ok: false,
            error: "Save As and exports are not supported in this session" });
        }
        say("Save rejected: this session can only overwrite the selected file", "err");
        break;
      }
      // The host's state is document-wide, while editor save tickets are
      // independent. Refuse overlapping writes so an older acknowledgement
      // cannot mark newer bytes clean or race Seafile's compare-and-swap.
      if (window.__saveInFlight) {
        dirtyRevision += 1;
        window.__lastDirty = true;
        window.__editorConfirmedSave = false;
        window.__saveConfirmationPending = false;
        fetch("/session/" + SID + "/dirty", {
          method: "POST", credentials: "same-origin",
          headers: { "Content-Type": "text/plain" }, body: "true",
        }).catch(() => {});
        if (ticket !== undefined && ticket !== null) {
          toCraft("saveResult", { ticket: ticket, ok: false, error: "another save is still in progress" });
        }
        say("Save not started; wait for the current save, then retry", "busy");
        break;
      }
      say("Saving…", "busy");
      window.__saveInFlight = true;
      window.__lastDirty = true;
      window.__editorConfirmedSave = false;
      window.__saveConfirmationPending = false;
      saveRevision = dirtyRevision;
      let ok = false;
      let error = "the save did not happen";
      let sessionUnavailable = false;
      try {
        const resp = await fetch("/session/" + SID + "/save", {
          method: "POST",
          credentials: "same-origin",
          headers: { "Content-Type": "application/octet-stream", "X-ArtCraft-Filename": FILE_NAME },
          body: bytes,
        });
        const result = await resp.json();
        sessionUnavailable = result.error ===
          "the editing session expired or is unavailable; return to Seafile and reopen the file";
        ok = !!resp.ok && result.ok === true;
        if (!ok) {
          error = result.error || ("HTTP " + resp.status);
        } else {
          error = "";
        }
        window.__lastSave = result;
        if (ok) {
          window.__saveConfirmationPending = true;
          say("Stored" + (result.version ? " — new version " + result.version : ""), "busy");
        } else {
          window.__lastDirty = true;
          say("Save failed: " + error, "err");
        }
      } catch (err) {
        error = err.message;
        window.__lastSave = { ok: false };
        window.__lastDirty = true;
        say("Save failed: " + error, "err");
      }
      // Tell the app how the save ended. Without this the app waits for a
      // confirmation that never comes and the document stays dirty forever.
      if (ticket !== undefined && ticket !== null) {
        // The app shows this message to the user, so it must not carry the
        // internals (paths, ids, upstream answers). The full error stays in the
        // host page's console and in the service's log.
        const shown = ok ? "" : (sessionUnavailable
          ? "this editing session expired or is unavailable; return to Seafile and reopen the file"
          : "the file could not be stored");
        toCraft("saveResult", { ticket: ticket, ok: ok, error: shown });
      }
      window.__saveInFlight = false;
      break;
    }

    case APP + ":dirty":
      if (data.dirty) {
        dirtyRevision += 1;
        window.__lastDirty = true;
        window.__editorConfirmedSave = false;
      } else if (window.__saveInFlight) {
        // Craft can report clean as soon as it starts its own save. Keep the
        // host dirty until the durable write and the editor's post-result
        // dirty=false acknowledgement have both happened.
        window.__lastDirty = true;
      } else if (window.__saveConfirmationPending && window.__lastSave?.ok === true) {
        // The editor's clean signal is accepted only after durable storage and
        // the host's response, and only if no newer dirty signal arrived while
        // those bytes were being stored.
        window.__lastDirty = dirtyRevision !== saveRevision;
        window.__editorConfirmedSave = !window.__lastDirty;
        window.__saveConfirmationPending = false;
      } else if (!window.__lastSave || window.__lastSave.ok === true) {
        window.__lastDirty = false;
      } else {
        window.__lastDirty = true;
      }
      // The gateway keeps the "not persisted" state, so the host can warn on
      // close and the service knows the document is unsaved.
      fetch("/session/" + SID + "/dirty", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "text/plain" },
        body: window.__lastDirty ? "true" : "false",
      }).catch(() => {});
      if (window.__lastDirty) {
        say("Unsaved changes", "busy");
      } else if (window.__editorConfirmedSave) {
        say("Saved" + (window.__lastSave.version ? " — new version " + window.__lastSave.version : ""), "ok");
      } else {
        say(FILE_NAME + " (no changes)", "ok");
      }
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


def render(sid, app, app_url, file_name, can_edit, csp_nonce=None):
    """Render the host page for one editing session."""
    return (
        _TEMPLATE
        .replace("__TITLE__", html.escape(file_name))
        .replace("__CSP_NONCE__", html.escape(csp_nonce or "", quote=True))
        .replace("__APP_URL__", html.escape(app_url, quote=True))
        .replace("__APP_NAME__", html.escape(app))
        .replace("__SID__", json.dumps(sid))
        .replace("__APP__", json.dumps(app))
        .replace("__CAN_EDIT__", "true" if can_edit else "false")
        .replace("__FILE_NAME__", json.dumps(file_name))
    )
