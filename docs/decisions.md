# Decisions

Why Lumbung is built the way it is. Newest last. Earlier entries describe designs that were replaced; they stay because they explain the current one.

## 2026-11-14: one shared repo instead of agents per repo

**Problem.** Good agents existed on one machine only, and new repos grew their own copies of agents that already existed elsewhere.

**Decision.** One git repo holds the shared agents, skills, rules and hooks, at user level, so every repo on a machine sees them.

**Why not one `.claude/` per repo?** That is how the duplicates started.

## 2026-11-14: the guard denies, with an override

A warning is easy to scroll past. A denial makes Claude look at the existing agent. `# lumbung-override: <reason>` keeps real exceptions cheap and records them in the file itself.

## 2026-11-14: core-template links to Lumbung

`security-reviewer`, `slop-reviewer`, `dependency-auditor` and their skills used to live in core-template. They are general, so their single source is now Lumbung. core-template links to them, and its sync script still writes real files into the public core repos, so those repos stay self-contained.

Side effect: those agents look for their skill in the repo first, then in the plugin, and diff against `dev` when it exists, else against the default branch.

## 2026-11-14 (replaced): install script, VM as hub, then any git remote

The first working version had `install.py` copy files into `~/.claude` and a SessionStart hook `git pull` the kit. Usage logs went over SSH to the VM, later onto a `usage` branch in git. It worked, but every machine needed a clone and a Python command to get started, and the hook did its own git work at every session start. Replaced by the next entry.

## 2026-11-14: a Claude Code plugin with its own marketplace

**Problem.** "Still complicated: I have to run Python." Setting up a machine should not need a clone or a script.

**Decision.** The repo is a plugin marketplace that lists one plugin, `lumbung`. Installing it is one command inside Claude Code. Claude Code downloads it, keeps it updated, and loads its agents, skills, command and hooks.

**What changed with it:**

- `install.py` and the sync hook are gone. Claude Code copies and updates the plugin.
- No `version` in `plugin.json`, so the version is the commit SHA and every push to `master` is a release.
- Rules arrive through a SessionStart hook, because a plugin cannot ship `CLAUDE.md`.
- Everything is namespaced: `lumbung:security-reviewer`.
- Develop mode is `claude --plugin-dir <clone>`. It replaces the installed plugin for that session only, so a branch never touches other machines and needs no reminder hook.
- The usage log stays on each machine, in the plugin's data folder. Merging logs across machines would need a clone or a service on every machine, which is the complication this step removed. Logs from other machines can still be passed to `report.py` by hand.

**Python stays, out of sight.** The guard and the logger are still Python, now started by `run.sh`, which picks whichever Python runs on the machine (`python3` on the VM, often `python` or `py -3` on Windows). Hooks run in shell form so this works in `sh` and Git Bash alike. Exec form would need one fixed executable name, and no single name exists on all three machines.

**Remote.** Private GitHub repo `mahrus-rohisyam/lumbung-agent`. The VM installs from its local clone until it has a GitHub key; a local-path marketplace loads the clone in place.

## Open

- **VM access to GitHub.** It has no GitHub credentials yet. Until it does, it installs from `/root/lumbung-agent` and runs whatever branch is checked out there.
- **Cross-machine usage.** Local only for now. If combined numbers turn out to matter, the old `usage` branch approach (in git history) is the starting point.
- **MCP servers** (openproject, codebase-memory) are not managed. Some are local binaries or hold credentials per machine. A plugin can ship MCP servers, so this can move into Lumbung later if it makes sense.
