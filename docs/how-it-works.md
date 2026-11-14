# How it works

## Repository layout

```
lumbung/
├── README.md
├── REGISTRY.md          # every agent and skill; the guard parses the Agents table
├── agents/              # kit agents       -> ~/.claude/agents/
├── skills/              # kit skills       -> ~/.claude/skills/
├── rules/CLAUDE.md      # rules block      -> ~/.claude/CLAUDE.md
├── hooks/
│   ├── common.py        # paths, git helper, registry and frontmatter parsing
│   ├── sync.py          # SessionStart
│   ├── guard_agent.py   # PreToolUse (Write|Edit|MultiEdit)
│   └── log_usage.py     # SubagentStart, SubagentStop
├── install.py
├── report.py
└── docs/
```

Branches: `master` (what every machine runs), `feature/*` (work in progress), `usage` (logs only; see below).

All scripts are Python standard library, so the same files run on Linux and Windows.

## Hooks

`install.py` registers each hook in the exec form, not as a shell string:

```json
{"type": "command", "command": "/usr/bin/python3", "args": ["/root/lumbung/hooks/sync.py"], "timeout": 30}
```

`command` is the Python that ran `install.py`, and `args` is the absolute path to the script. No shell sits in between, so quoting and Windows path problems do not arise. The codebase-memory-mcp hooks already in `settings.json` use the same form.

| Event | Matcher | Script | Timeout |
|---|---|---|---|
| SessionStart | `startup` | `sync.py` | 30 s |
| PreToolUse | `Write\|Edit\|MultiEdit` | `guard_agent.py` | 10 s |
| SubagentStart | `*` | `log_usage.py` | 5 s |
| SubagentStop | `*` | `log_usage.py` | 5 s |

Every script catches its own errors and exits quietly. A broken Lumbung must never break a session.

## Sync (`sync.py`)

At each new session (`startup` only, not resume or compact):

1. If the clone has an `origin`, `git fetch origin` (8 s limit).
2. On `master`: fast-forward to `origin/master`. Local commits that are not pushed are kept; if the branches have diverged, nothing happens until you sort it out by hand.
3. On any other branch: no update. It prints a develop-mode reminder, which Claude sees at the start of the session.
4. If `HEAD` differs from the commit recorded at the last install, it runs `install.py --quiet`. When the update came from the remote, it prints a one-line summary of the new commits.
5. Publishes this machine's usage log (below).

Git runs with `GIT_TERMINAL_PROMPT=0` and no stdin, so it fails instead of waiting for a password.

Agents are read when a session starts, so an update becomes visible in the next session after the one that pulled it. That one session of lag is the price of not slowing every session down with a second pass.

## Duplicate guard (`guard_agent.py`)

Runs before every Write, Edit or MultiEdit. It does nothing unless the target is `*/.claude/agents/*.md` or this repo's `agents/*.md`. For those files, it works out the file's content after the edit, reads its frontmatter, and decides:

| Situation | Result |
|---|---|
| The file is an installed copy in `~/.claude/agents` that came from Lumbung | **Deny**: edit the kit instead |
| The file already exists and keeps its `name` (an ordinary edit) | Allow |
| The `name` is already used by another agent file the guard can see | **Deny** |
| The `name` is in the registry for a different location | **Deny** |
| The description overlaps strongly with an existing agent | **Deny**, naming the agent and the shared terms |
| The frontmatter has `# lumbung-override: <reason>` | Skip the three checks above |
| The `name` is not in the registry | Allow, and tell Claude to add a registry row |

**Agents it can see:** this repo's `agents/`, `~/.claude/agents/`, and the `.claude/agents/` of every repo path in the registry that exists on this machine. On Windows the VM's repo paths do not exist, so for repo-bound agents only the registry row is checked. That is why every agent needs a row.

**Registered first is fine.** If the registry row for the name points to where the file is being written (`kit` and the target is `agents/`, or the target is inside the row's repo path), the name check passes. You can add the row before writing the file.

**Overlap measure:** words of three or more letters from the name, description and registry Purpose, minus common stop words, each cut to its first six letters (a crude stem, so `review`, `reviewer` and `reviews` match). The score is shared terms divided by the size of the smaller set. A block needs a score of 0.5 or more and at least three shared terms. Both values are constants at the top of the file. In testing it caught a "code security auditor", an "AI slop checker" and a "social content" agent against `security-reviewer`, `slop-reviewer` and `marketer`, and let a report writer and a DB migration agent through.

The guard is a speed bump, not a lock. Claude or a person can always write the file another way. The registry and the rules in `CLAUDE.md` matter as much as the hook.

## Usage logging

**Recording (`log_usage.py`).** Each SubagentStart and SubagentStop appends one line to `~/.claude/lumbung/usage.jsonl`:

```json
{"ts": "2026-11-14T09:12:03Z", "host": "laptop", "event": "start", "agent": "slop-reviewer",
 "agent_id": "a1b2", "session": "…", "cwd": "C:\\work\\report"}
```

Built-in agents are logged too (`Explore`, `Plan`, `general-purpose`), so you can see how much custom agents are used next to them.

**Publishing (in `sync.py`).** Each machine owns one file on the `usage` branch: `usage/<host>.jsonl`, holding that machine's whole log. At session start, sync:

1. stores the local log as a git blob,
2. stops if `origin/usage` (or the local `usage` branch when there is no remote) already has exactly that content,
3. otherwise builds a commit on top of that tip that replaces only its own file, using a temporary index, so the working tree and the current branch are never touched,
4. pushes `usage` to `origin`.

Machines never write each other's files, so there are no merge conflicts. If a push is rejected because another machine pushed first, the next session rebuilds on the new tip. The log only grows, and replacing the whole file means a lost push loses nothing.

On the VM-as-remote setup, Windows machines push `usage` into the VM repo, and the VM's own sync commits its file onto that same local branch.

**Reporting (`report.py`).** Fetches `origin`, then reads this machine's local log plus every other `usage/<host>.jsonl` from `origin/usage` (or local `usage`). Prints runs per agent with last use, machines and top repos ("repo" is the last folder of `cwd`), then three lists: registry entries unused in the period, agents used in two or more repos that have no registry row, and agents used in three or more repos.

## Install manifest

`~/.claude/lumbung/manifest.json` lists the agent and skill names the last install put in place. The next install removes names that left the kit and replaces the ones still there. Files in `~/.claude/agents` and `~/.claude/skills` that are not in the manifest are never touched, apart from the warned-about name clash described in [setup.md](setup.md).
