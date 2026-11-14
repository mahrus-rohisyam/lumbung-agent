# Lumbung

One shared store of Claude Code subagents, skills, rules and hooks for every machine I work on.

A *lumbung* is the rice barn a village shares: everyone stores in it and takes from it, so nobody keeps their own pile. Lumbung does the same for agents. A good agent written on the VM is there on the laptop next session, and a new repo uses the agent that already exists instead of growing its own copy.

## What it does

- **Same kit everywhere.** Agents and skills live in this repo. `install.py` copies them into `~/.claude`, and a SessionStart hook pulls and reinstalls whenever `master` moves.
- **No duplicate agents.** A PreToolUse hook checks every new `.claude/agents/*.md` against [REGISTRY.md](REGISTRY.md) and the agents it can see, and blocks near copies.
- **Usage you can see.** SubagentStart/SubagentStop hooks log which agent ran, on which machine, in which repo. `report.py` summarizes all machines.
- **Safe to develop in.** Only `master` is shared. A new agent is built on a `feature/*` branch and tried on one machine first.

## Machines

| Machine | OS | Used for |
|---|---|---|
| VM | Linux | Main development; the laptop and PC usually connect to it |
| Laptop | Windows | Reports and marketing; heavier work when the VM is short on resources |
| PC | Windows | Windows app development; heavier work when the VM is short on resources |

Each machine clones this repo and runs `install.py`. They all sync through the `origin` remote, which can be the VM over SSH or a private GitHub/GitLab repo. See [docs/setup.md](docs/setup.md).

## Quick start

```bash
# VM
python3 /root/lumbung/install.py --host vm
```

```powershell
# Laptop or PC (PowerShell)
git clone <origin-url> $HOME\lumbung
python $HOME\lumbung\install.py --host laptop   # or --host pc
```

Then start a new Claude Code session. `/agents` lists the kit's agents.

## Everyday commands

| Task | Command |
|---|---|
| Install or refresh by hand | `python install.py` |
| See who uses what | `python report.py --days 30` |
| Start a new agent or skill | `git switch -c feature/<name>`, then [docs/workflow.md](docs/workflow.md) |
| Remove Lumbung from a machine | `python install.py --uninstall` |

## What's in the kit

| Agents | Skills |
|---|---|
| `security-reviewer`, `slop-reviewer`, `dependency-auditor` | `secure-coding`, `code-slop`, `no-ai-slop`, `dependency-check` |

Repo-bound agents (for example `marketer` in `/root/marketing`) stay in their repo and are listed in [REGISTRY.md](REGISTRY.md).

## Documentation

- [docs/setup.md](docs/setup.md): installing on each machine, choosing the remote, credentials, uninstalling
- [docs/workflow.md](docs/workflow.md): adding, developing, releasing and retiring agents and skills
- [docs/how-it-works.md](docs/how-it-works.md): files, hooks, the duplicate guard, sync and usage logging in detail
- [docs/troubleshooting.md](docs/troubleshooting.md): common problems and fixes
- [docs/decisions.md](docs/decisions.md): why it is built this way, and what is still open
