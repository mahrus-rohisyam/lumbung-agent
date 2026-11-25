---
name: docker-deploy
description: Write and review Dockerfiles, docker-compose configurations, and container deployment setups for production readiness. Use when containerizing an app, optimizing image size, hardening runtime security, or debugging container lifecycle and networking.
---

# Docker & container deploy

Produce small, reproducible, hardened container images and reliable compose/runtime configurations.

## 1. Dockerfile hygiene

- **Multi-stage builds:** Separate build/compile dependencies from the final runtime stage so compilers, package managers, and source artifacts do not ship to production.
- **Minimal, pinned base images:** Use slim, alpine, or distroless base images pinned to an explicit version tag and preferably image digest (`@sha256:...`). Avoid `:latest`.
- **Layer & cache order:** Copy dependency manifests (`go.mod`/`go.sum`, `package*.json`, `pyproject.toml`) and install dependencies *before* copying application source.
- **`.dockerignore`:** Always include a `.dockerignore` excluding `.git`, `.env*`, `node_modules`, build artifacts, logs, and local secrets so they never enter the build context or layers.
- **Non-root user:** Create and switch to a dedicated non-root `USER` before `ENTRYPOINT`/`CMD`.

## 2. Runtime & lifecycle safety

- **PID 1 & graceful shutdown:** Use exec-form `ENTRYPOINT`/`CMD` (`["./app"]`, not shell form) so `SIGTERM` reaches the application directly for graceful shutdown.
- **Healthchecks:** Define a lightweight `HEALTHCHECK` (or orchestrator readiness/liveness probe) checking real app readiness without leaking sensitive data.
- **Immutable & bounded:** Support read-only root filesystems where possible (mount `/tmp` or writable dirs explicitly), set memory/CPU limits in compose/orchestration, and drop unnecessary Linux capabilities (`cap_drop: [ALL]`).
- **Logging:** Write logs to `stdout`/`stderr` in structured format; do not log inside container files that grow unbounded.

## 3. Configuration, secrets & networking

- **Build vs. runtime:** Never bake secrets into `ARG`, `ENV`, `COPY`, or image layers. Inject secrets at runtime via environment files excluded from git or orchestrator secret mounts.
- **Network binding:** Expose only necessary ports; bind services behind a reverse proxy on loopback (`127.0.0.1`) or an internal Docker network rather than `0.0.0.0` on public hosts.
- **Persistence:** Use named volumes or explicit host mounts for stateful data; keep application containers stateless.

## 4. Review checklist

Before shipping a container change:
- Is `.dockerignore` present and excluding `.git`, `.env`, and local secrets?
- Does the final image run as non-root from a pinned minimal base?
- Are `SIGTERM` handling, `HEALTHCHECK`, and resource limits configured?
- Are all secrets kept out of build layers and `Dockerfile` `ENV`/`ARG`?
