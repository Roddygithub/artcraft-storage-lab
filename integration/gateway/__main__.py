"""Run the ArtCraft gateway.

    ARTCRAFT_SEAFILE_URL=https://seafile.example.org \\
    ARTCRAFT_SEAFILE_TOKEN=... \\
    python3 -m gateway --host 127.0.0.1 --port 8777

The token is an account token for the Seafile user the service acts as. It is
read from the environment and never written to disk.
"""

import argparse
import os
import sys

if __package__ in (None, ""):  # allow "python3 integration/gateway/__main__.py"
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gateway.server import serve  # noqa: E402
from gateway.seafile import Seafile  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="ArtCraft gateway for Seafile")
    parser.add_argument("--host", default=os.environ.get("ARTCRAFT_GATEWAY_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("ARTCRAFT_GATEWAY_PORT", "8777")))
    parser.add_argument("--dispatch", default=None, help="path to dispatch.json")
    args = parser.parse_args()

    kwargs = {}
    if args.dispatch:
        kwargs["dispatch_path"] = args.dispatch
    serve(host=args.host, port=args.port, seafile=Seafile.from_env(), **kwargs)


if __name__ == "__main__":
    main()
