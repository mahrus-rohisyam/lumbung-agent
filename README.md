# Lumbung

A plugin for **Claude Code** and **Antigravity** that gives every machine you work on the same subagents, skills and rules, stops new repos from growing duplicate agents, and records which agents actually get used.

A *lumbung* is the rice barn a village shares: everyone stores in it and takes from it, so nobody keeps their own pile. Lumbung does the same for agents. A good agent written on one machine is available on every other machine next session, and a new repo uses the agent that already exists instead of growing its own copy.

**Why it exists:** When you work across multiple machines, the agent you need is always on another machine, every new repo grows its own copies of agents that already exist, and you have no visibility into which agents actually get used. Turning the shared kit into a Claude Code plugin lets Claude Code install and update it automatically without manual scripts. The full story is in [docs/background.md](docs/background.md).

## Install

Fork this repository to manage your own shared agents and registry, or install directly from `<owner>/lumbung-agent`.

### Claude Code

On each machine, in a Claude Code session:

```
/plugin install lumbung --marketplace <owner>/lumbung-agent
```

Then turn on updates once: `/plugin` → **Marketplaces** → `lumbung-agent` → **Enable auto-update**.

That's all. No Python commands to run, nothing to clone. If your fork is a private repo, each machine needs non-interactive git access to it; see [docs/setup.md](docs/setup.md).

### Antigravity

On each machine, clone into Antigravity's global plugins folder so it works across every workspace:

```bash
# Linux / macOS
git clone https://github.com/mahrus-rohisyam/lumbung-agent ~/.gemini/config/plugins/lumbung
```

```powershell
# Windows (PowerShell)
git clone https://github.com/mahrus-rohisyam/lumbung-agent $HOME\.gemini\config\plugins\lumbung
```

That's all — Antigravity loads `plugin.json`, `hooks.json`, `rules/AGENTS.md`, `skills/`, and `agents/` automatically on the next turn. Update anytime with `git -C ~/.gemini/config/plugins/lumbung pull`. See [docs/setup.md](docs/setup.md#install-antigravity) for workspace-only or symlink installs.

## What you get

| | |
|---|---|
| Subagents | `lumbung:security-reviewer`, `lumbung:slop-reviewer`, `lumbung:dependency-auditor` |
| Skills | `lumbung:secure-coding`, `lumbung:code-quality`, `lumbung:code-slop`, `lumbung:no-ai-slop`, `lumbung:dependency-check`, `lumbung:marketing`, `lumbung:ads-making`, `lumbung:seo-audit` |
| Command | `/lumbung:report`: which subagents ran on this machine, how often, in which repos |
| Rules | Loaded into every session: check the registry before making an agent, where new agents go |
| Duplicate guard | Blocks a new agent file that copies an existing agent |
| Usage log | Every subagent run on this machine, kept in the plugin's data folder |

Repo-bound agents (for example a project-specific agent in `~/projects/my-app`) stay in their repo and are listed in [REGISTRY.md](REGISTRY.md).

## Everyday use

| Task | How |
|---|---|
| Use an agent | Ask for it, or let Claude pick it: "review this with lumbung:security-reviewer" |
| See what gets used | `/lumbung:report` (add a number of days: `/lumbung:report 90`) |
| Get updates now | `/plugin` → **Marketplaces** → `lumbung-agent` → **Update marketplace** |
| Build a new agent or skill | Clone your repo, work on a branch, try it with `claude --plugin-dir`: [docs/workflow.md](docs/workflow.md) |

## Documentation

- [docs/background.md](docs/background.md): why Lumbung exists, and how the design evolved
- [docs/setup.md](docs/setup.md): install on each machine, private repo access, updates, removal
- [docs/workflow.md](docs/workflow.md): add, develop, release and retire agents and skills
- [docs/how-it-works.md](docs/how-it-works.md): plugin layout, hooks, the duplicate guard and the usage log in detail
- [docs/troubleshooting.md](docs/troubleshooting.md): common problems and fixes
- [docs/decisions.md](docs/decisions.md): why it is built this way, and what is still open
- [REGISTRY.md](REGISTRY.md): every agent and skill, and where it lives
