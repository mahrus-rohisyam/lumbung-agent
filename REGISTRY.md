# Registry

Every subagent and skill in your setup, what it does and where it lives. Read this before creating a new one.

The duplicate guard (`hooks/guard_agent.py`) parses the **Agents** table, so keep its shape: four columns, the agent name in the first column, repo paths in backticks. The Purpose column is compared with new agents' descriptions to detect overlap, so write it in plain English with the words a similar agent would use.

**Location values**

- `kit`: a file in this repo's `agents/` or `skills/`, shipped by the `lumbung` plugin to every machine (as `lumbung:<name>`).
- ``repo: `<path>` ``: lives only in that repo (e.g. ``repo: `~/projects/my-app` ``). The guard also scans that repo's `.claude/agents/` when the path exists on the machine.
- `plugin: <name>`: installed by another tool or plugin. Do not edit it or copy it into the kit.

**Status values:** `active`, `draft` (on a feature branch, not on `master` yet), `retired` (kept so the name is not reused by accident).

Names in the tables are the bare names from each file's frontmatter, without the `lumbung:` prefix.

## Agents

| Name | Purpose | Location | Status |
|---|---|---|---|
| security-reviewer | Read-only security review of a finished change: input handling, auth, sessions, authorization, SQL, files, redirects, secrets | kit | active |
| slop-reviewer | Read-only review of a diff for AI slop in code, docs, comments, commit messages, UI copy | kit | active |
| dependency-auditor | Vet a package or module before adding or bumping a dependency | kit | active |

## Skills

| Name | Purpose | Location | Status |
|---|---|---|---|
| secure-coding | Secure coding rules and checks for backend and web apps (used by security-reviewer) | kit | active |
| code-slop | AI-slop patterns in code across languages (used by slop-reviewer) | kit | active |
| no-ai-slop | Slop patterns in prose; upstream petergyang/no-ai-slop | kit | active |
| dependency-check | Dependency vetting procedure (used by dependency-auditor) | kit | active |
| code-quality | Code correctness, modularity, readability, edge cases, and testability review | kit | active |
| marketing | Marketing strategy, positioning, messaging, and campaign planning | kit | active |
| ads-making | Ad creation covering videography (scripts, shot lists, pacing) and copywriting (angles, variations, CTAs) | kit | active |
| seo-audit | Technical, on-page, and content SEO strategy and checking | kit | active |
| ci-cd | CI/CD pipeline design, supply-chain hardening, caching, and release gates | kit | active |
| docker-deploy | Dockerfile, docker-compose, and container runtime hardening | kit | active |
| report | `/lumbung:report`: subagent usage on this machine (a command, listed here so the name stays taken) | kit | active |
