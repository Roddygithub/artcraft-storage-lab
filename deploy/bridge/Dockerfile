# The WOPI editor bridge as a container: stdlib Python, no dependencies.
# Build from the repository root:  docker build -f deploy/bridge/Dockerfile -t craft-bridge .
FROM python:3.12-slim
WORKDIR /app
COPY bridge/ /app/bridge/
# Editor bundles and editors.json are mounted at runtime (see compose.yml); nothing is baked in.
ENV BRIDGE_BIND=0.0.0.0 BRIDGE_PORT=8778 BRIDGE_EDITORS=/config/editors.json BRIDGE_STATIC_DIR=/editors
EXPOSE 8778
USER nobody
CMD ["python3", "-m", "bridge"]
