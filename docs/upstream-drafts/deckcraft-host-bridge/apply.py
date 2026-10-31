import pathlib, re, sys
root = pathlib.Path(sys.argv[1])
m = root / "apps/deckcraft-web/src/main.rs"
s = m.read_text()
if "mod host;" not in s:
    s = s.replace('#[cfg(target_arch = "wasm32")]\nmod web;', '#[cfg(target_arch = "wasm32")]\nmod host;\n#[cfg(target_arch = "wasm32")]\nmod web;')
    s = s.replace("//! URL query flags: `?webgl`", "//! URL query flags: `?host=parent` turns on the parent-page bridge (`host.rs`); `?webgl`")
    m.write_text(s)
c = root / "apps/deckcraft-web/Cargo.toml"
cs = c.read_text()
if '"MessageEvent"' not in cs:
    cs = cs.replace('"CssStyleDeclaration"]', '"CssStyleDeclaration", "MessageEvent"]')
    c.write_text(cs)
w = root / "apps/deckcraft-web/src/web.rs"
s = w.read_text()
if "use crate::host;" in s:
    print("web.rs already patched; nothing to do")
    sys.exit(0)
s = s.replace("use deckcraft_ui_egui::{Inbox, InboxEvent, InboxFile, Services, SlideApp};",
              "use deckcraft_ui_egui::{Inbox, InboxEvent, InboxFile, Services, SlideApp};\n\nuse crate::host;")
s = s.replace("""        let result = eframe::WebRunner::new()
            .start(
                canvas,
                options,
                Box::new(move |cc| {""",
"""        // `?host=parent`: a same-origin parent page keeps the files; it sends the presentation
        // and receives every save. Without a parent on this origin the bridge is `None` and the
        // page behaves as before.
        let bridge = if query().contains("host=parent") { host::Bridge::new() } else { None };
        let bridge_for_app = bridge.clone();
        let result = eframe::WebRunner::new()
            .start(
                canvas,
                options,
                Box::new(move |cc| {""")
s = s.replace("""                    let inbox: Inbox = Inbox::default();
                    let mut app = SlideApp::new(Session::new(), services(inbox.clone(), cc.egui_ctx.clone()));
                    let q = query();
                    if !q.contains("blank") {""",
"""                    let inbox: Inbox = Inbox::default();
                    let mut services = services(inbox.clone(), cc.egui_ctx.clone());
                    let host_files: host::HostFiles = host::HostFiles::default();
                    if let Some(b) = &bridge_for_app {
                        b.connect(&mut services, host_files.clone(), cc.egui_ctx.clone());
                    }
                    let mut app = SlideApp::new(Session::new(), services);
                    let q = query();
                    if bridge_for_app.is_some() {
                        // The host sends the document; start empty, not with the sample deck.
                        if let Err(e) = app.run("file.new", serde_json::json!({})) {
                            log::error!("new presentation: {e}");
                        }
                    } else if !q.contains("blank") {""")
s = s.replace("""                    Ok(Box::new(WebShell { app, inbox }))""",
"""                    Ok(Box::new(WebShell { app, inbox, host: bridge_for_app.map(|b| (b, host_files)) }))""")
s = s.replace("""            match result {
                Ok(()) => el.remove(),
                Err(e) => el.set_inner_html(&format!("<p>DeckCraft failed to start: {e:?}</p><p>A browser with WebGPU or WebGL2 is required.</p>")),
            }""",
"""            match result {
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
                    el.set_inner_html(&format!("<p>DeckCraft failed to start: {e:?}</p><p>A browser with WebGPU or WebGL2 is required.</p>"));
                }
            }""")
s = s.replace("""struct WebShell {
    app: SlideApp,
    inbox: Inbox,
}""", """struct WebShell {
    app: SlideApp,
    inbox: Inbox,
    /// The parent-page bridge and the files it sent, in host mode.
    host: Option<(host::Bridge, host::HostFiles)>,
}""")
s = s.replace("""    fn logic(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        self.app.logic(ctx);
    }""", """    fn logic(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // Files from the host page open like dropped presentations, with a fresh request id.
        if let Some((_, files)) = &self.host {
            let pending: Vec<(String, Vec<u8>)> = files.borrow_mut().drain(..).collect();
            for (name, bytes) in pending {
                let id = self.app.begin_external_file("drop");
                push_inbox(&self.inbox, InboxEvent::File(InboxFile { id, name, bytes }));
            }
        }
        self.app.logic(ctx);
    }""")
w.write_text(s)
print(("ok   " if '"MessageEvent"' in c.read_text() else "MISS ") + "web-sys MessageEvent feature")
for needle in ("use crate::host;", "host::Bridge::new()", "b.connect(", "host: bridge_for_app", "b.post_ready()", "begin_external_file(\"drop\")"):
    print(("ok   " if needle in s else "MISS ") + needle)
