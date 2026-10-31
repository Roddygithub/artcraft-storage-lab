import pathlib, sys
root = pathlib.Path(sys.argv[1])
m = root / "apps/designcraft-web/src/main.rs"
s = m.read_text()
if "mod host;" not in s:
    s = s.replace('#[cfg(target_arch = "wasm32")]\nmod web;', '#[cfg(target_arch = "wasm32")]\nmod host;\n#[cfg(target_arch = "wasm32")]\nmod web;', 1)
    m.write_text(s)
c = root / "apps/designcraft-web/Cargo.toml"
cs = c.read_text()
if '"MessageEvent"' not in cs:
    cs = cs.replace('features = ["Event",', 'features = ["Event", "MessageEvent",', 1)
    c.write_text(cs)
w = root / "apps/designcraft-web/src/web.rs"
s = w.read_text()
if "use crate::host;" in s:
    print("web.rs already patched; nothing to do"); sys.exit(0)
s = s.replace("use designcraft_ui_egui::{DesignApp, ImportRequest, ImportedFile, Inbox, Services};",
              "use designcraft_ui_egui::{DesignApp, ImportRequest, ImportedFile, Inbox, Services};\n\nuse crate::host;", 1)
s = s.replace("""        let runner = eframe::WebRunner::new();
        let creator_graphics = graphics.clone();""", """        let runner = eframe::WebRunner::new();
        let creator_graphics = graphics.clone();
        // `?host=parent`: a same-origin parent page keeps the files; it sends the document and
        // receives every save. Without a parent on this origin the bridge is `None` and the page
        // behaves as before (downloads).
        let bridge = if query().contains("host=parent") { host::Bridge::new() } else { None };
        let bridge_for_app = bridge.clone();""")
s = s.replace("""                    let inbox: Inbox = Inbox::default();
                    let mut app = DesignApp::new(Session::new(), services(inbox.clone(), cc.egui_ctx.clone()));
                    if has_query_flag(&query(), "sample") {
                        let _ = app.run("file.newSample", serde_json::json!({}));
                    }
                    Ok(Box::new(WebShell { app, inbox, graphics: creator_graphics }))""",
"""                    let inbox: Inbox = Inbox::default();
                    let mut services = services(inbox.clone(), cc.egui_ctx.clone());
                    let host_files: host::HostFiles = host::HostFiles::default();
                    if let Some(b) = &bridge_for_app {
                        b.connect(&mut services, host_files.clone(), cc.egui_ctx.clone());
                    }
                    let mut app = DesignApp::new(Session::new(), services);
                    if has_query_flag(&query(), "sample") {
                        let _ = app.run("file.newSample", serde_json::json!({}));
                    }
                    Ok(Box::new(WebShell { app, inbox, graphics: creator_graphics, host: bridge_for_app.map(|b| (b, host_files)) }))""")
s = s.replace("""            .await;
        match result {
            Ok(()) => {
                if let Err(e) = install_recovery_controls(&runner, &canvas, &graphics) {""",
"""            .await;
        if let Some(b) = &bridge {
            match &result {
                Ok(()) => b.post_ready(),
                Err(e) => b.post_failed(&format!("{e:?}")),
            }
        }
        match result {
            Ok(()) => {
                if let Err(e) = install_recovery_controls(&runner, &canvas, &graphics) {""")
s = s.replace("""struct WebShell {
    app: DesignApp,
    inbox: Inbox,
    graphics: GraphicsState,
}""", """struct WebShell {
    app: DesignApp,
    inbox: Inbox,
    graphics: GraphicsState,
    /// The parent-page bridge and the files it sent, in host mode.
    host: Option<(host::Bridge, host::HostFiles)>,
}""")
s = s.replace("""    fn logic(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        let graphics = self.graphics.clone();
        let _ = graphics.run_if_healthy(|| self.app.logic(ctx));
    }""", """    fn logic(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        let graphics = self.graphics.clone();
        let _ = graphics.run_if_healthy(|| {
            // Files from the host page open like dropped ones, with a fresh import request.
            if let Some((_, files)) = &self.host {
                let pending: Vec<(String, Vec<u8>)> = files.borrow_mut().drain(..).collect();
                for (name, bytes) in pending {
                    let request = self.app.import_request("drop");
                    self.inbox.lock().unwrap_or_else(|e| e.into_inner()).push(ImportedFile { request, name, bytes });
                }
            }
            self.app.logic(ctx)
        });
    }""")
w.write_text(s)
for needle in ("use crate::host;", "host::Bridge::new()", "b.connect(&mut services", "host: bridge_for_app", "b.post_ready()", "import_request(\"drop\");\n                    self.inbox"):
    print(("ok   " if needle in s else "MISS ") + needle.splitlines()[0])
