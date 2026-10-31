import pathlib, sys
root = pathlib.Path(sys.argv[1])
m = root / "apps/photocraft-web/src/main.rs"
s = m.read_text()
if "mod host;" not in s:
    s = s.replace('#[cfg(target_arch = "wasm32")]\nmod web;', '#[cfg(target_arch = "wasm32")]\nmod host;\n#[cfg(target_arch = "wasm32")]\nmod web;', 1)
    m.write_text(s)
c = root / "apps/photocraft-web/Cargo.toml"
cs = c.read_text()
if '"MessageEvent"' not in cs:
    cs = cs.replace('features = ["Window",', 'features = ["Window", "MessageEvent",', 1)
    c.write_text(cs)
w = root / "apps/photocraft-web/src/web.rs"
s = w.read_text()
if "use crate::host;" in s:
    print("web.rs already patched; nothing to do"); sys.exit(0)
s = s.replace("use wasm_bindgen::JsCast as _;", "use wasm_bindgen::JsCast as _;\n\nuse crate::host;", 1)
s = s.replace("""        let pen_target = canvas.clone();
        let result = eframe::WebRunner::new()""", """        let pen_target = canvas.clone();
        // `?host=parent`: a same-origin parent page keeps the files; it sends the document and
        // receives every save. Without a parent on this origin the bridge is `None` and the page
        // behaves as before (downloads).
        let bridge = if q.contains("host=parent") { host::Bridge::new() } else { None };
        let bridge_for_app = bridge.clone();
        let result = eframe::WebRunner::new()""")
s = s.replace("""                    let mut app = PhotocraftApp::new(session, services(inbox.clone(), place_inbox.clone(), drag_pos_service(pen_target.clone(), drag)));""",
"""                    let mut services = services(inbox.clone(), place_inbox.clone(), drag_pos_service(pen_target.clone(), drag));
                    if let Some(b) = &bridge_for_app {
                        b.connect(&mut services, inbox.clone(), cc.egui_ctx.clone());
                    }
                    let mut app = PhotocraftApp::new(session, services);""")
s = s.replace("""                    Ok(Box::new(WebShell { app, inbox, place_inbox, unsaved, served, database, presets, ui_language: "" }))""",
"""                    Ok(Box::new(WebShell { app, inbox, place_inbox, unsaved, served, database, presets, ui_language: "", host: bridge_for_app, host_dirty: None }))""")
s = s.replace("""            match result {
                Ok(()) => el.remove(),
                Err(e) => el.set_inner_html(&format!("<p>PhotoCraft failed to start: {e:?}</p><p>A browser with WebGPU or WebGL2 is required.</p>")),
            }""", """            match result {
                Ok(()) => {
                    el.remove();
                    if let Some(b) = &bridge {
                        b.post_ready();
                    }
                }
                Err(e) => {
                    if let Some(b) = &bridge {
                        b.post_failed(&format!("{e:?}"));
                    }
                    el.set_inner_html(&format!("<p>PhotoCraft failed to start: {e:?}</p><p>A browser with WebGPU or WebGL2 is required.</p>"));
                }
            }""")
s = s.replace("""    /// The interface language whose served script font was last asked for.
    ui_language: &'static str,
}""", """    /// The interface language whose served script font was last asked for.
    ui_language: &'static str,
    /// The parent-page bridge in host mode, and the dirty state last reported to it.
    host: Option<host::Bridge>,
    host_dirty: Option<bool>,
}""")
s = s.replace("""        self.serve_fonts(ctx);
        self.app.logic_frame(ctx, frame);
        self.save_presets(ctx);""", """        self.serve_fonts(ctx);
        self.app.logic_frame(ctx, frame);
        self.save_presets(ctx);
        if let Some(b) = &self.host {
            let dirty = self.app.has_unsaved_work();
            if self.host_dirty != Some(dirty) {
                b.post_dirty(dirty);
                self.host_dirty = Some(dirty);
            }
        }""")
w.write_text(s)
for needle in ("use crate::host;", "host::Bridge::new()", "b.connect(&mut services", "host: bridge_for_app", "b.post_ready()", "b.post_dirty(dirty)"):
    print(("ok   " if needle in s else "MISS ") + needle)
