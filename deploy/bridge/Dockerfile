# The WOPI editor bridge as a container: stdlib Python, no dependencies.
# Build from the repository root:  docker build -f deploy/bridge/Dockerfile -t craft-bridge .
# Multi-stage: build stage installs gunicorn, final stage copies only what's needed (~45 MB).

# ---- Build stage ----
FROM python:3.12-slim AS builder
WORKDIR /install
RUN pip install --no-cache-dir --prefix=/install gunicorn==23.0.0

# ---- Runtime stage ----
FROM python:3.12-slim
WORKDIR /app

# Copy gunicorn from builder
COPY --from=builder /install /usr/local

# Create non-root user
RUN groupadd -r -g 1000 appgroup && useradd -r -g appgroup -u 1000 -m -d /home/app appuser

# Copy bridge source
COPY --chown=appuser:appgroup bridge/ /app/bridge/

# Editor bundles and editors.json are mounted at runtime (see compose.yml); nothing is baked in.
ENV BRIDGE_BIND=0.0.0.0 BRIDGE_PORT=8778 BRIDGE_EDITORS=/config/editors.json BRIDGE_STATIC_DIR=/editors
EXPOSE 8778

USER appuser

# gunicorn: bounded workers/threads, header timeouts; long request timeout for large PutFile + commit.
# Access logs are disabled: request queries/referrers may contain WOPI capabilities.
# --max-requests prevents memory leaks; --worker-tmp-dir /dev/shm uses tmpfs for worker heartbeats.
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8778", \
     "--workers", "2", \
     "--threads", "8", \
     "--timeout", "600", \
     "--graceful-timeout", "30", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--worker-tmp-dir", "/dev/shm", \
     "bridge.wsgi:application"]
