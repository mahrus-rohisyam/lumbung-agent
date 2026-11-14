# Lumbung

A Claude Code plugin that gives every machine I work on the same subagents, skills and rules, stops new repos from growing duplicate agents, and records which agents actually get used.

A *lumbung* is the rice barn a village shares: everyone stores in it and takes from it, so nobody keeps their own pile. Lumbung does the same for agents. A good agent written on the VM is on the laptop next session, and a new repo uses the agent that already exists instead of growing its own copy.

**Why it exists:** I work on a VM, a laptop and a PC. The agent I needed was always on the other machine, every new repo grew its own copies of agents that already existed, and I had no idea which agents were actually used. The first fix still meant running Python scripts by hand on every machine, so it became a plugin that Claude Code installs and updates by itself. The full story is in [docs/background.md](docs/background.md).

## Install

On each machine, in a Claude Code session:

```
/plugin install lumbung --marketplace mahrus-rohisyam/lumbung-agent
```

Then turn on updates once: `/plugin` → **Marketplaces** → `lumbung-agent` → **Enable auto-update**.

That's all. No Python to run, nothing to clone. The repo is private, so the machine needs git access to it; see [docs/setup.md](docs/setup.md).

## What you get

| | |
|---|---|
| Subagents | `lumbung:security-reviewer`, `lumbung:slop-reviewer`, `lumbung:dependency-auditor` |
| Skills | `lumbung:secure-coding`, `lumbung:code-slop`, `lumbung:no-ai-slop`, `lumbung:dependency-check` |
| Command | `/lumbung:report`: which subagents ran on this machine, how often, in which repos |
| Rules | Loaded into every session: check the registry before making an agent, where new agents go |
| Duplicate guard | Blocks a new agent file that copies an existing agent |
| Usage log | Every subagent run on this machine, kept in the plugin's data folder |

Repo-bound agents (for example `marketer` in `/root/marketing`) stay in their repo and are listed in [REGISTRY.md](REGISTRY.md).

## Everyday use

| Task | How |
|---|---|
| Use an agent | Ask for it, or let Claude pick it: "review this with lumbung:security-reviewer" |
| See what gets used | `/lumbung:report` (add a number of days: `/lumbung:report 90`) |
| Get updates now | `/plugin` → **Marketplaces** → `lumbung-agent` → **Update marketplace** |
| Build a new agent or skill | Clone this repo, work on a branch, try it with `claude --plugin-dir`: [docs/workflow.md](docs/workflow.md) |

## Documentation

- [docs/background.md](docs/background.md): why I built this, and how the design got where it is
- [docs/setup.md](docs/setup.md): install on each machine, access to the private repo, updates, removal
- [docs/workflow.md](docs/workflow.md): add, develop, release and retire agents and skills
- [docs/how-it-works.md](docs/how-it-works.md): plugin layout, hooks, the duplicate guard and the usage log in detail
- [docs/troubleshooting.md](docs/troubleshooting.md): common problems and fixes
- [docs/decisions.md](docs/decisions.md): why it is built this way, and what is still open
- [REGISTRY.md](REGISTRY.md): every agent and skill, and where it lives
