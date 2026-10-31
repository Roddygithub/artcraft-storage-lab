# The WOPI editor bridge as a container: stdlib Python, no dependencies.
# Build from the repository root:  docker build -f deploy/bridge/Dockerfile -t craft-bridge .
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir gunicorn==23.0.0
COPY bridge/ /app/bridge/
# Editor bundles and editors.json are mounted at runtime (see compose.yml); nothing is baked in.
ENV BRIDGE_BIND=0.0.0.0 BRIDGE_PORT=8778 BRIDGE_EDITORS=/config/editors.json BRIDGE_STATIC_DIR=/editors
EXPOSE 8778
USER nobody
# gunicorn: bounded workers/threads, header timeouts; long request timeout for large PutFile + commit.
CMD ["gunicorn", "--bind", "0.0.0.0:8778", "--workers", "2", "--threads", "8", "--timeout", "600", "--graceful-timeout", "30", "--access-logfile", "-", "bridge.wsgi:application"]
