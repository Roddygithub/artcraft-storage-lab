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

frame.addEventListener("message", async (event) => {
  // Both checks: the origin AND the source window. A page on our origin that is
  // not our frame must not be able to inject bytes or claim a save.
  if (event.origin !== ORIGIN) return;
  if (event.source !== frame.contentWindow) return;
  const data = event.data;
  if (!data || typeof data !== "object") return;

  switch (data.type) {
    case APP + ":ready":
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
      say("Saving…", "busy");
      try {
        const resp = await fetch("/session/" + SID + "/save", {
          method: "POST",
          credentials: "same-origin",
          headers: { "Content-Type": "application/octet-stream" },
          body: bytes,
        });
        const result = await resp.json();
        if (!resp.ok || !result.ok) {
          say("Save failed: " + (result.error || resp.status), "err");
        } else {
          say("Saved — new version " + (result.version || ""), "ok");
        }
      } catch (err) {
        say("Save failed: " + err.message, "err");
      }
      break;
    }

    case APP + ":dirty":
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
        .replace("__FILE_NAME__", html.escape(file_name))
    )
