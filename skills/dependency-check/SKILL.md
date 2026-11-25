---
name: dependency-check
description: Vet a third-party package or module before adding, upgrading or writing code against it. Use when a change would add a direct dependency, bump a version, run npx/uvx/go install, or call a library API you have not read at the pinned version. Covers existence (hallucinated or typosquatted names), maintenance, license, vulnerabilities, install scripts, release age and API verification.
---

# Dependency check

Every dependency is code you ship without writing or reviewing it. Package names that an AI made up get registered by attackers ("slopsquatting"), and popular packages have been hijacked to publish malicious releases. This check runs before adding or installing any package, and before you write code against an API you have not read.

## 1. Do we need it?

Answer in order and stop at the first yes:

1. Does the standard library do it? (e.g. Go: `net/http`, `log/slog`, `crypto/*`, `encoding/*`, `slices`, `maps`; Web/Node: `fetch`, `URL`, `Intl`, `crypto.subtle`, `structuredClone`; Python: `pathlib`, `urllib`, `dataclasses`, `json`, `tomllib`.)
2. Does the project or its shared internal modules already provide it? Search the codebase first.
3. Does an existing dependency in the project's manifest (`go.mod`, `package.json`, `pyproject.toml`, `Cargo.toml`, etc.) already do it?
4. Is it under about 50 lines that we can own and test? Then write it.

Only a "no" to all four leads to step 2.

## 2. Verify the package

Run registry, deps.dev and OSV queries for the target ecosystem (`go`, `npm`, `pypi`, `cargo`, `maven`, `nuget`); do not answer from memory.

**Go module**

```sh
curl -s https://proxy.golang.org/<module>/@latest              # exists, latest version and its time
go list -m -versions <module>                                  # all versions
curl -s https://api.deps.dev/v3/systems/go/packages/<url-escaped-module>   # versions, licenses, links
curl -s https://api.osv.dev/v1/query -d '{"package":{"name":"<module>","ecosystem":"Go"},"version":"<v>"}'
```

**npm package**

```sh
npm view <pkg> name version license repository.url maintainers dependencies scripts --json
npm view <pkg> time --json                                     # publish date of every version
curl -s https://api.deps.dev/v3/systems/npm/packages/<pkg>     # includes OpenSSF Scorecard when known
curl -s https://api.osv.dev/v1/query -d '{"package":{"name":"<pkg>","ecosystem":"npm"},"version":"<v>"}'
```

**PyPI package**

```sh
curl -s https://pypi.org/pypi/<pkg>/json                       # metadata, release dates, license, links
curl -s https://api.deps.dev/v3/systems/pypi/packages/<pkg>
curl -s https://api.osv.dev/v1/query -d '{"package":{"name":"<pkg>","ecosystem":"PyPI"},"version":"<v>"}'
```

Reject, or bring to the user as a risk, when any of these hold:

| Check | Pass |
|---|---|
| Name | Exactly the package the docs or repo name; no near-miss spelling, no unexpected scope |
| Source | Registry metadata links to a public repo, and that repo publishes this package |
| Age of the version | Published at least 14 days ago (time for a hijacked release to be caught) |
| Maintenance | A release or commit in the last 12 months, or a small library that is clearly finished |
| Vulnerabilities | No known vulnerability without a fixed version you are taking |
| License | MIT, BSD-2/3, Apache-2.0, ISC or MPL-2.0. Anything else (GPL, AGPL, SSPL, none) needs a maintainer's approval |
| Install scripts | Lifecycle scripts (`preinstall`/`install`/`postinstall`, `setup.py`) need a clear reason; disable install scripts by default where supported |
| Weight | Transitive dependency count is proportionate to what it does |

## 3. Ask for approval

Never add a direct dependency without approval from the person you are working for or a maintainer. Present one short card:

```
Add <name>@<exact version>?
Why: <the job it does in this change>
Rejected alternatives: <stdlib / project code / existing dep / own code, and why each is not enough>
Checks: published <date>, license <x>, <n> transitive deps, vulns <none / fixed in v>, install scripts <none / what>
Risk: <anything that did not pass, or "none found">
```

## 4. Add it

- Pin exact versions (e.g. `npm install --save-exact`, `go get <module>@<version>`, exact version pins in lockfiles). Never commit `@latest`.
- Commit the lockfile (`go.sum`, `package-lock.json`, `uv.lock`, `Cargo.lock`, etc.) in the same commit.
- If the project keeps a dependency log (for example `docs/dependencies.md`), add a row: package, version, why, approved by, date.
- Run the stack's verification and audit commands (e.g. `go mod tidy && go mod verify && govulncheck ./...`, `npm audit --omit=dev`, `pip-audit`).

For JavaScript/TypeScript repositories, a `.npmrc` can enforce most of these defaults:

```ini
save-exact=true        # pin exact versions
min-release-age=14     # refuse versions published less than 14 days ago
ignore-scripts=true    # never run dependency install scripts
allow-git=none         # no dependencies from git URLs
engine-strict=true
```

If a package is needed sooner than 14 days after a release (for example a security fix), add it to `min-release-age-exclude` with a comment and maintainer approval.

## 5. Before writing code against it

Read the API at the version in the lockfile, not the one you remember:

- Go: `go doc <pkg>.<Symbol>` or the source under `$(go env GOMODCACHE)`.
- TypeScript/JavaScript: the package's `.d.ts` in `node_modules/<pkg>/`, and its CHANGELOG for breaking changes between the version you know and the pinned one.
- Python/other ecosystems: inspect the installed package source or stubs in the environment, and check its CHANGELOG.

If a function or option you planned to use does not exist at that version, say so. Do not invent a shim around it.

## Upgrades

Same checks, plus: read the changelog between the two versions, run the full test suite, and keep one dependency bump per commit so a bad one can be reverted alone.
