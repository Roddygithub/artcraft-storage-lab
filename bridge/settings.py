"""Configuration from the environment, shared by `python -m bridge` and `bridge.wsgi`."""

import os

from .app import Config, load_editors


def config_from_env() -> Config:
    """Raises KeyError/ValueError/OSError on a bad configuration."""
    return Config(
        public_url=os.environ["BRIDGE_PUBLIC_URL"],
        seahub_origin=os.environ["BRIDGE_SEAHUB_ORIGIN"],
        editors=load_editors(os.environ.get("BRIDGE_EDITORS", "bridge/editors.example.json")),
        static_dir=os.environ.get("BRIDGE_STATIC_DIR") or None,
    )
