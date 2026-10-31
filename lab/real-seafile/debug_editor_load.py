#!/usr/bin/env python3
"""Load one editor bundle standalone (no Seahub) in headless Chromium and log every request,
failure and console line, to tell a bundle problem from a bridge/Seahub problem.
Usage inside the browser container: python3 lab/real-seafile/debug_editor_load.py <editor-id> [seconds]"""
import os, sys, time
from playwright.sync_api import sync_playwright

editor = sys.argv[1]
budget = int(sys.argv[2]) if len(sys.argv) > 2 else 120
BRIDGE = os.environ["BRIDGE_URL"].rstrip("/")
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--enable-webgl", "--disable-dev-shm-usage"])
    page = b.new_page(viewport={"width": 1200, "height": 800})
    t0 = time.time()
    page.on("request", lambda r: print(f"[{time.time()-t0:5.1f}s] REQ  {r.method} {r.url[-90:]}", flush=True))
    page.on("requestfailed", lambda r: print(f"[{time.time()-t0:5.1f}s] FAIL {r.url[-90:]} {r.failure}", flush=True))
    page.on("response", lambda r: print(f"[{time.time()-t0:5.1f}s] RESP {r.status} {r.url[-90:]}", flush=True))
    page.on("console", lambda m: print(f"[{time.time()-t0:5.1f}s] CON  [{m.type}] {m.text[:200]}", flush=True))
    page.on("pageerror", lambda e: print(f"[{time.time()-t0:5.1f}s] ERR  {e}", flush=True))
    page.goto(f"{BRIDGE}/editors/{editor}/index.html", wait_until="commit", timeout=60000)
    end = time.time() + budget
    while time.time() < end:
        has = page.evaluate(f"typeof window['{editor}'] === 'object'")
        if has:
            print(f"[{time.time()-t0:5.1f}s] window.{editor} present", flush=True)
            try:
                print("commands():", str(page.evaluate(f"window['{editor}'].commands().then(c => Array.isArray(c) ? c.length : Object.keys(c).length)"))[:100], flush=True)
            except Exception as e:
                print("commands() failed:", e, flush=True)
            break
        time.sleep(2)
    page.screenshot(path=os.path.join(os.environ.get("RESULTS_DIR", "."), f"debug-{editor}.png"))
    b.close()
