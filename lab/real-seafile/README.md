# Real-Seafile lab

A stock Seafile CE 13 + ONLYOFFICE Docs CE + the bridge + upstream Craft web bundles, in a
dedicated Lima VM with Docker. Nothing here touches a production system; the VM is disposable.

## Run

```bash
limactl start --name=seafile-lab --cpus=4 --memory=4 --disk=30 --tty=false template:docker
```

```bash
lab/real-seafile/up.sh up          # sync files into the VM, pull images, start db/redis/seafile/onlyoffice/bridge
```

```bash
lab/real-seafile/up.sh configure   # append the managed Seahub settings block, restart Seafile
```

```bash
lab/real-seafile/up.sh slice       # HTTP slice (run_slice.py) → results/slice.json
```

```bash
lab/real-seafile/up.sh browser     # headless Chromium slice (run_browser.py) → results/browser.json + screenshots
```

`up.sh down` stops the stack; `limactl delete seafile-lab` removes the VM. Secrets are generated
into `.env` inside the VM on first `up` and never leave it.

Editor bundles live under `static/<editor-id>/` (gitignored) with a `static/<editor-id>-PROVENANCE.txt`
(tag, SHA-256, and whether the lab changed anything). `editors.json` maps extensions to editors;
`seahub_settings.extra.py` is the managed block `configure` writes.

The VM has a Rust/wasm toolchain (`rustup`, `trunk`) for building patched bundles under `~/build/`;
4 GiB of RAM is enough for one `trunk build --release` with `CARGO_BUILD_JOBS=2` while ONLYOFFICE
is stopped.

## Human checklist (HTTPS, desktop browser) — not yet run

The slices run headless over plain HTTP, so they cannot see these. Run against a deployment from
`deploy/bridge/` behind TLS, in Chrome/Edge and Firefox:

1. Open a `.docx` from Seafile Web: WordCraft appears inside the Seafile page, the host bar shows
   the file name and `ready`; no `frame-ancestors` or CSP error in the console.
2. Renderer: the console says WebGPU (not the WebGL2 fallback) on HTTPS.
3. Type, see the host bar say `unsaved changes`; press Ctrl/Cmd+S; the bar says `saved to Seafile`
   and Seafile's history shows a new version by you.
4. Close the tab with unsaved changes: the browser's leave-page prompt appears.
5. Clipboard: copy/paste text within the editor and from another app.
6. Open the same file in a second tab, save there, then save in the first: the first gets
   `the file changed in Seafile since it was opened` and nothing is overwritten.
7. Share the library read-only with another user; for them the bar says `read-only` and Ctrl+S
   is refused.
8. Wait past `WOPI_ACCESS_TOKEN_EXPIRATION`; a save then says the token expired; reopen works.
9. `.pdf` opens Seafile's viewer; the `?edit_pdf=true` URL opens PdfCraft.
10. `.pptx` still opens in ONLYOFFICE.
