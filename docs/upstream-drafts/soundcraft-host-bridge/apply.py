import pathlib, sys
root = pathlib.Path(sys.argv[1])
m = root / "apps/soundcraft-web/src/main.rs"
s = m.read_text()
if "mod host;" not in s:
    s = s.replace('#[cfg(target_arch = "wasm32")]\nmod web;', '#[cfg(target_arch = "wasm32")]\nmod host;\n#[cfg(target_arch = "wasm32")]\nmod web;', 1)
    m.write_text(s)
c = root / "apps/soundcraft-web/Cargo.toml"
cs = c.read_text()
if '"MessageEvent"' not in cs:
    cs = cs.replace('"CssStyleDeclaration"]', '"CssStyleDeclaration", "MessageEvent"]')
    c.write_text(cs)
w = root / "apps/soundcraft-web/src/web.rs"
s = w.read_text()
if "use crate::host;" in s:
    print("web.rs already patched; nothing to do"); sys.exit(0)
s = s.replace("use wasm_bindgen::JsCast as _;", "use wasm_bindgen::JsCast as _;\n\nuse crate::host;", 1)
s = s.replace("""    eframe::WebLogger::init(log::LevelFilter::Info).ok();
    io::set_deliver(download);""",
"""    eframe::WebLogger::init(log::LevelFilter::Info).ok();
    // `?host=parent`: a same-origin parent page keeps the files; it sends the session and
    // receives every save. Without a parent on this origin the bridge is `None` and the page
    // behaves as before (downloads).
    let bridge = if query().contains("host=parent") { host::Bridge::new() } else { None };
    io::set_deliver(if bridge.is_some() { host::deliver } else { download });
    let bridge_for_app = bridge.clone();""")
s = s.replace("""                    let engine = if query().contains("empty") { Engine::default() } else { soundcraft_engine::demo::demo_engine() };
                    let player = soundcraft_playback::Player::new(Arc::new(engine.session().clone()));
                    let app = SoundApp::new(engine, Some(player), Services::default());
                    Ok(Box::new(WebShell { app, inbox: Rc::default(), samples: Rc::default() }))""",
"""                    // The host sends the session: start empty, not with the demo.
                    let engine = if bridge_for_app.is_some() || query().contains("empty") { Engine::default() } else { soundcraft_engine::demo::demo_engine() };
                    let player = soundcraft_playback::Player::new(Arc::new(engine.session().clone()));
                    let app = SoundApp::new(engine, Some(player), Services::default());
                    let host_files: host::HostFiles = host::HostFiles::default();
                    if let Some(b) = &bridge_for_app {
                        b.connect(host_files.clone(), cc.egui_ctx.clone());
                    }
                    Ok(Box::new(WebShell { app, inbox: Rc::default(), samples: Rc::default(), host: bridge_for_app.map(|b| (b, host_files)) }))""")
s = s.replace("""            match result {
                Ok(()) => el.remove(),
                Err(e) => el.set_inner_html(&format!("<p>SoundCraft failed to start: {e:?}</p><p>A browser with WebGPU or WebGL2 is required.</p>")),
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
                    el.set_inner_html(&format!("<p>SoundCraft failed to start: {e:?}</p><p>A browser with WebGPU or WebGL2 is required.</p>"));
                }
            }""")
s = s.replace("""struct WebShell {
    app: SoundApp,
    inbox: Inbox,
    samples: SampleInbox,
}""", """struct WebShell {
    app: SoundApp,
    inbox: Inbox,
    samples: SampleInbox,
    /// The parent-page bridge and the files it sent, in host mode.
    host: Option<(host::Bridge, host::HostFiles)>,
}""")
s = s.replace("""        self.take_drops(ctx);
        self.take_path_prompt(ctx);
        let pending = std::mem::take(&mut *self.inbox.borrow_mut());""",
"""        self.take_drops(ctx);
        self.take_path_prompt(ctx);
        // Files from the host page go where their extension says, like dropped files.
        if let Some((_, files)) = &self.host {
            let from_host: Vec<(String, Vec<u8>)> = files.borrow_mut().drain(..).collect();
            for (name, bytes) in from_host {
                self.inbox.borrow_mut().push((Purpose::of(&name), name, bytes));
            }
        }
        let pending = std::mem::take(&mut *self.inbox.borrow_mut());""")
w.write_text(s)
for needle in ("use crate::host;", "host::Bridge::new()", "host::deliver", "b.connect(", "host: bridge_for_app", "b.post_ready()", "Purpose::of(&name), name, bytes));\n            }"):
    print(("ok   " if needle in s else "MISS ") + needle.splitlines()[0])
