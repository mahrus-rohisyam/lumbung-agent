# Decisions

Why Lumbung is built the way it is. Newest last.

## 2026-11-14: one repo, copied into `~/.claude`

**Problem.** Good agents existed on one machine only, and new repos grew their own copies of agents that already existed elsewhere.

**Decision.** One git repo holds the shared agents, skills, rules and hooks. `install.py` copies them into the user-level `~/.claude`, which every repo on the machine sees.

**Why not symlinks into `~/.claude`?** Symlinks need extra privileges or developer mode on Windows, and a symlinked agent changes under a running session when you switch branches. A copy changes only when you install.

**Why not one `.claude/` per repo?** That is how the duplicates started.

## 2026-11-14: Python standard library, exec-form hooks

Two machines run Windows. Python is installed everywhere, and the standard library avoids per-machine package setup. Hooks are registered as `command` + `args`, so no shell parses them on any OS.

## 2026-11-14: the guard denies, with an override

A warning is easy to scroll past. A denial makes Claude look at the existing agent. `# lumbung-override: <reason>` keeps real exceptions cheap and documents them in the file itself.

## 2026-11-14: core-template links to Lumbung

`security-reviewer`, `slop-reviewer`, `dependency-auditor` and their skills used to live in core-template. They are general, so their single source is now Lumbung. core-template links to them, and its sync script still writes real files into the public core repos, so those repos stay self-contained.

Side effect: those agents now find their skill in the repo or in `~/.claude/skills`, and diff against `dev` when it exists, else against the default branch.

## 2026-11-14: sync through any git remote; usage on its own branch

The first version shipped logs to the VM over SSH and treated the VM as a hub. That tied every machine to the VM being up and reachable. Now each machine only talks to its `origin` remote, which can be the VM or a private GitHub/GitLab repo, with no code change.

Usage logs go on a separate `usage` branch with one file per machine, written through a temporary index. `master` stays free of log noise, machines never conflict, and no service runs anywhere.

## 2026-11-14: only `master` is shared

New agents are built on `feature/*` branches. On a branch, sync does not pull and reminds you at every session start. A half-finished agent can never spread to the other machines, and dropping an idea is just switching back to `master`.

## Open

- **Remote:** stay on the VM, or move to private GitHub or GitLab? Moving is in [setup.md](setup.md#moving-to-github-or-gitlab). It needs a key or credential on each machine, the VM included (it has no GitHub credentials today).
- **MCP servers** (openproject, codebase-memory) are not managed. Some are local binaries or hold credentials per machine. For now they are listed in the registry only.
