# Registry

Every subagent and skill I use, what it does and where it lives. Read this before creating a new one.

The duplicate guard (`hooks/guard_agent.py`) parses the **Agents** table, so keep its shape: four columns, the agent name in the first column, repo paths in backticks. The Purpose column is compared with new agents' descriptions to detect overlap, so write it in plain English with the words a similar agent would use.

**Location values**

- `kit`: a file in this repo's `agents/` or `skills/`, shipped by the `lumbung` plugin to every machine (as `lumbung:<name>`).
- ``repo: `<path>` ``: lives only in that repo (path as on the VM). The guard also scans that repo's `.claude/agents/` when the path exists on the machine.
- `plugin: <name>`: installed by another tool. Do not edit it or copy it into the kit.

**Status values:** `active`, `draft` (on a feature branch, not on `master` yet), `retired` (kept so the name is not reused by accident).

Names in the tables are the bare names from each file's frontmatter, without the `lumbung:` prefix.

## Agents

| Name | Purpose | Location | Status |
|---|---|---|---|
| security-reviewer | Read-only security review of a finished change: input handling, auth, sessions, authorization, SQL, files, redirects, secrets | kit (also synced into core-backend, core-frontend by core-template) | active |
| slop-reviewer | Read-only review of a diff for AI slop in code, docs, comments, commit messages, UI copy | kit (also synced into core-backend, core-frontend by core-template) | active |
| dependency-auditor | Vet a Go module or npm package before adding or bumping a dependency | kit (also synced into core-backend, core-frontend by core-template) | active |
| marketer | Plan, write and render marketing content per brand: videos, landing loops, social images | repo: `/root/marketing` | active, needs the marketing repo |
| codebase-memory | Code knowledge graph verification for a task | plugin: codebase-memory-mcp | active |
| codebase-memory-scout | Fast code knowledge graph lookup | plugin: codebase-memory-mcp | active |
| codebase-memory-auditor | Bounded code knowledge graph audit | plugin: codebase-memory-mcp | active |

## Skills

| Name | Purpose | Location | Status |
|---|---|---|---|
| secure-coding | Secure coding rules for Go + React (used by security-reviewer) | kit | active |
| code-slop | Slop patterns in Go and TypeScript code (used by slop-reviewer) | kit | active |
| no-ai-slop | Slop patterns in prose; upstream petergyang/no-ai-slop, pinned in core-template's `skills-lock.json` | kit | active |
| dependency-check | Dependency vetting procedure (used by dependency-auditor) | kit | active |
| campaign, content-radar, new-brand, refresh, retro | Marketing workflow | repo: `/root/marketing` | active |
| report | `/lumbung:report`: subagent usage on this machine (a command, listed here so the name stays taken) | kit | active |
| codebase-memory | How to use the code knowledge graph | plugin: codebase-memory-mcp | active |
| reverse-engineer-anything | Reverse engineering with REA | plugin: rea | active |
| (synced) | Skills from the claude.ai account, synced by the account itself | `~/.claude/skills/synced` | do not touch |
