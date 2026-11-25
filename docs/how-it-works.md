# How it works

## Repository layout

The repo is both a marketplace and the one plugin it lists.

```
lumbung-agent/
├── plugin.json             # Antigravity native plugin manifest
├── hooks.json              # Antigravity lifecycle hooks (PreToolUse duplicate guard)
├── .claude-plugin/
│   ├── marketplace.json    # Claude Code marketplace "lumbung-agent", plugin "lumbung"
│   └── plugin.json         # Claude Code plugin manifest; no version, tracks commits
├── agents/                 # subagents      -> lumbung:<name>
├── skills/                 # skills         -> lumbung:<name>
├── commands/report.md      # /lumbung:report (Claude Code)
├── hooks/
│   ├── hooks.json          # Claude Code hook registrations
│   ├── run.sh              # finds a working Python, then runs a hook script
│   ├── common.py           # paths, registry and frontmatter parsing
│   ├── guard_agent.py      # duplicate guard (Claude Code + Antigravity payloads)
│   └── log_usage.py        # usage log (Claude Code SubagentStart/SubagentStop)
├── rules/AGENTS.md         # rules text loaded into every session
├── scripts/report.py       # usage summary
├── REGISTRY.md
└── docs/
```

Branches: `master` is the release. `feature/*` is work in progress.

## Installing and updating

Claude Code does both. On install it copies the plugin into `~/.claude/plugins/cache/lumbung-agent/lumbung/<version>/`, where `<version>` is the first 12 characters of the commit SHA. With auto-update on for the marketplace, it re-checks the remote in the background after a session starts. A new commit means a new version: a new cache folder, loaded from the next session on. Old version folders are removed 14 days later.

A marketplace added from a local directory path behaves differently. The plugin is loaded **in place** from that folder at every session start, with no copy and no version check.

## Hooks

`hooks/hooks.json` registers four hooks. Claude Code substitutes `${CLAUDE_PLUGIN_ROOT}` with the plugin's folder.

| Event | Matcher | Runs | Timeout |
|---|---|---|---|
| SessionStart | `startup\|resume\|clear\|compact` | `cat rules/rules.md` | 5 s |
| PreToolUse | `Write\|Edit\|MultiEdit` | `guard_agent.py` | 10 s |
| SubagentStart | `*` | `log_usage.py` | 5 s |
| SubagentStop | `*` | `log_usage.py` | 5 s |

**Rules.** In Antigravity, `rules/AGENTS.md` is loaded automatically while the plugin is enabled. In Claude Code, a `SessionStart` hook prints `rules/AGENTS.md` to stdout (`startup|resume|clear|compact`), so the rules arrive after `/clear` and compaction as well.

**Running Python on Linux, macOS and Windows.** The hooks are shell-form commands (`sh run.sh <script>`). On Linux and macOS they run in `sh`, on Windows in Git Bash. `run.sh` tries `python3`, `python` and `py -3` in turn. It runs a one-line check with each and uses the first that passes, because on Windows `python3` is often the Microsoft Store stub that exists but does not run anything. It then `exec`s the script with the hook input still on stdin. If no Python works, it exits 0 and the hook does nothing. Exec form (`command` + `args`) would avoid the shell, but it needs one fixed executable name, and no single name exists across all operating systems.

Every Python script catches its own errors and exits 0. A broken Lumbung must never break a session.

## Duplicate guard (`guard_agent.py`)

Runs before every Write, Edit or MultiEdit:

| Situation | Result |
|---|---|
| The target is under `~/.claude/plugins/cache/` or `~/.claude/plugins/marketplaces/` | **Deny**: that copy is managed by Claude Code; edit the clone |
| The target is not an agent file | Allow, no checks |
| The file exists and keeps its `name` (an ordinary edit) | Allow |
| The `name` is used by another agent file the guard can see | **Deny** |
| The `name` is in the registry for a different location | **Deny** |
| The description overlaps strongly with an existing agent | **Deny**, naming the agent and the shared terms |
| The frontmatter has `# lumbung-override: <reason>` | Skip the three checks above |
| The `name` is not in the registry | Allow, and tell Claude to add a registry row |

**Agent files:** `*/.claude/agents/*.md`, and `agents/*.md` in any folder that has `.claude-plugin/plugin.json`, such as a Lumbung clone.

**Agents it can see:** the plugin's own `agents/` (the installed copy, or the clone under `--plugin-dir`), `~/.claude/agents/`, and the `.claude/agents/` of every repo path in the registry that exists on this machine. If a listed repo path does not exist on the current machine (for example a Linux path checked on Windows), only its registry row is checked. That is why every agent needs a row.

**Registered first is fine.** If the registry row for the name points where the file is being written (`kit` and the target is the `agents/` folder of the `lumbung` plugin, or the target is inside the row's repo path), the name check passes. You can add the row before writing the file.

**Overlap measure:** words of three or more letters from the name, description and registry Purpose, minus common stop words, each cut to its first six letters (a crude stem, so `review`, `reviewer` and `reviews` match). The score is shared terms divided by the size of the smaller set. A block needs a score of at least 0.5 and at least three shared terms. Both are constants at the top of the file. In testing it caught a "code security auditor" and an "AI slop checker" against `security-reviewer` and `slop-reviewer`, and let a report writer and a DB migration agent through.

The guard is a speed bump, not a lock: a file can always be written another way. The registry and the rules matter as much as the hook.

## Usage log

`log_usage.py` appends one line per SubagentStart and SubagentStop to `usage.jsonl` in the plugin's data folder, `${CLAUDE_PLUGIN_DATA}` (`~/.claude/plugins/data/lumbung-lumbung-agent/`). That folder survives plugin updates and is deleted on uninstall unless you pass `--keep-data`.

```json
{"ts": "2026-11-14T15:28:52Z", "host": "devbox", "event": "start", "agent": "Explore",
 "agent_id": "a1b2c3d4e5f60001", "session": "00000000-0000-0000-0000-000000000001", "cwd": "/home/user/projects/my-app"}
```

`agent` is the subagent type as Claude Code reports it: `lumbung:slop-reviewer` for this plugin's agents, plain names for built-in (`Explore`, `Plan`, `general-purpose`) and repo agents.

The log stays on the machine. `/lumbung:report` runs `scripts/report.py`, which prints runs per agent with last use, machine and top repos ("repo" is the last folder of `cwd`). It then lists registry entries unused in the period, agents used in two or more repos that have no registry row, and agents used in three or more repos. To look across machines, copy other machines' `usage.jsonl` files over and pass them as extra arguments:

```bash
python3 scripts/report.py --days 90 laptop-usage.jsonl desktop-usage.jsonl
```
