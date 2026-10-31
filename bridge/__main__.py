"""Run the bridge with the stdlib WSGI server (development only).

    BRIDGE_PUBLIC_URL=https://craft.example \
    BRIDGE_SEAHUB_ORIGIN=https://seafile.example \
    BRIDGE_EDITORS=bridge/editors.example.json \
    BRIDGE_STATIC_DIR=integration/static \
    python3 -m bridge

Behind a real reverse proxy, run it with any WSGI server (gunicorn, waitress).
"""

import os
import sys
import socketserver
from wsgiref.simple_server import WSGIServer, make_server


class _ThreadedServer(socketserver.ThreadingMixIn, WSGIServer):
    """One thread per request: a browser slowly consuming an 80 MB wasm bundle must not block the
    relay calls (or the editor's own scripts) of every other tab. The bridge holds no shared mutable
    state, so this is safe. For production put gunicorn or a reverse proxy in front anyway."""
    daemon_threads = True
    allow_reuse_address = True


from .app import Bridge, Config, load_editors


def main() -> int:
    try:
        cfg = Config(
            public_url=os.environ["BRIDGE_PUBLIC_URL"],
            seahub_origin=os.environ["BRIDGE_SEAHUB_ORIGIN"],
            editors=load_editors(os.environ.get("BRIDGE_EDITORS", "bridge/editors.example.json")),
            static_dir=os.environ.get("BRIDGE_STATIC_DIR") or None,
        )
    except (KeyError, ValueError, OSError) as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2
    host = os.environ.get("BRIDGE_BIND", "127.0.0.1")
    port = int(os.environ.get("BRIDGE_PORT", "8778"))
    with make_server(host, port, Bridge(cfg), server_class=_ThreadedServer) as srv:
        print(f"bridge listening on http://{host}:{port}  (public {cfg.public_url}, seahub {cfg.seahub_origin})")
        srv.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
