"""WSGI entry point: `gunicorn bridge.wsgi:application` (see deploy/bridge/Dockerfile)."""

from .app import Bridge
from .settings import config_from_env

application = Bridge(config_from_env())
