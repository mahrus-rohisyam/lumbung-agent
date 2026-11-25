# Decisions

Why Lumbung is built the way it is. Earlier entries describe designs that were replaced; they stay because they explain the current one.

## One shared repo instead of agents per repo

**Problem.** Good agents existed on one machine only, and new repos grew their own copies of agents that already existed elsewhere.

**Decision.** One Git repo holds the shared agents, skills, rules, and hooks at user level, so every repo on a machine sees them.

**Why not one `.claude/` per repo?** That is how the duplicates start.

## The guard denies, with an override

A warning is easy to scroll past. A denial makes Claude look at the existing agent. `# lumbung-override: <reason>` keeps real exceptions cheap and records them in the file itself.

## Portable skill lookup and diff base

Shipped reviewer agents look for their skill in the current repository first (`.agents/skills/<name>/SKILL.md`) and fall back to the plugin copy (`${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`), and diff against `dev` when it exists, else against the default branch. That lets the same agent definitions work cleanly both when installed via the plugin and when vendored into standalone repositories.

## Replaced: install script, central host as hub, then manual git sync

An earlier version had an install script copy files into `~/.claude` and a SessionStart hook `git pull` the kit, with usage logs synced over SSH or onto a dedicated `usage` branch. It worked, but every machine needed a clone and a manual Python setup command, and the hook ran git operations on every session start. Replaced by the plugin model below.

## A Claude Code plugin with its own marketplace

**Problem.** Setting up a machine should not require cloning a repo or running a setup script by hand.

**Decision.** The repo is a plugin marketplace that lists one plugin, `lumbung`. Installing it is one command inside Claude Code. Claude Code downloads it, keeps it updated, and loads its agents, skills, commands, and hooks.

**What changed with it:**

- No manual install script or sync hook. Claude Code copies and updates the plugin.
- No `version` in `plugin.json`, so the version is the commit SHA and every push to `master` is a release.
- Rules arrive through a SessionStart hook, because a plugin cannot ship `CLAUDE.md`.
- Everything is namespaced: `lumbung:security-reviewer`.
- Develop mode is `claude --plugin-dir <clone>`. It replaces the installed plugin for that session only, so a branch never touches other machines and needs no reminder hook.
- The usage log stays on each machine, in the plugin's data folder. Merging logs across machines would need a clone or a service on every machine, which is the complication this step removed. Logs from other machines can still be passed to `report.py` by hand.

**Python stays, out of sight.** The guard and the logger are still Python, started by `run.sh`, which picks whichever Python runs on the machine (`python3` on Linux/macOS, often `python` or `py -3` on Windows). Hooks run in shell form so this works in `sh` and Git Bash alike. Exec form would need one fixed executable name, and no single name exists across all operating systems.

**Remote.** Any Git remote (public or private) or a local directory path. A local-path marketplace loads the clone in place.

## Open

- **Cross-machine usage.** Local only for now. If combined numbers across machines matter, you can pass multiple `usage.jsonl` files to `scripts/report.py`, or build an automated sync layer later.
- **MCP servers.** Not managed here, since many require local binaries or per-machine credentials. A plugin can ship MCP servers, so this can move into Lumbung later if it makes sense.
