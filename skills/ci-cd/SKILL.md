---
name: ci-cd
description: Design, review, and harden CI/CD pipelines (GitHub Actions, GitLab CI, etc.). Use when writing or auditing workflow files, build/test/release automation, supply-chain security in CI, caching, or deployment gates.
---

# CI/CD

Build fast, deterministic, and least-privilege CI/CD pipelines. Review both workflow YAML and the scripts/actions they invoke.

## 1. Security & supply chain

- **Pin third-party actions / steps:** Pin external actions to a full 40-char commit SHA with a version comment (e.g. `uses: actions/checkout@<sha> # v4`), not a mutable branch or tag.
- **Least-privilege permissions:** Declare explicit `permissions:` at workflow or job level (e.g. `contents: read`); never leave default write-all token permissions.
- **Untrusted triggers:** Never run `pull_request_target` or `workflow_run` with checked-out PR code and secrets/write tokens. Treat PR titles, branch names, and issue bodies as untrusted input (never interpolate `${{ github.event.* }}` directly into `run:` shell commands; pass via `env:`).
- **Secrets & OIDC:** Prefer short-lived OIDC tokens over long-lived cloud keys. Never echo secrets, print full env dumps, or upload `.env` / credential files as artifacts.

## 2. Speed & reliability

- **Fail-fast order:** Run fast static checks (`lint`, `typecheck`, `format`) and unit tests before heavy builds, container pushes, or integration suites.
- **Concurrency:** Cancel superseded runs on feature branches (`concurrency: { group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true }`), while never cancelling production deploys mid-flight.
- **Caching:** Key dependency caches on lockfile hashes (`package-lock.json`, `go.sum`, `uv.lock`, `Cargo.lock`). Do not cache across untrusted PRs into protected branches.
- **Reproducibility:** Use frozen/locked installs (`npm ci`, `uv sync --frozen`, `go test` with committed `go.sum`) and explicit tool/runtime versions.

## 3. Release & deployment gates

- **Environment separation:** Protect production deployments with branch restrictions, environment approvals, and distinct secrets from staging/dev.
- **Artifact promotion:** Build and scan the artifact (or container image by digest) once, then promote the same artifact across environments rather than rebuilding per stage.
- **Rollback path:** Keep previous release tags/digests available and verify the rollback step is documented or automated.

## 4. Review checklist

Before finalizing a workflow change:
- Are all external actions pinned by commit SHA and token `permissions` scoped?
- Is any untrusted event payload interpolated directly into a shell script?
- Are timeouts (`timeout-minutes`) set on jobs so hung runners do not burn quota?
- Does the pipeline run security/dependency checks (`gitleaks`, `trivy`, `npm audit` / `govulncheck`) where applicable?
