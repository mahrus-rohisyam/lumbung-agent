# Working with agents and skills

The rule behind everything here: **`master` is what every machine runs.** Anything unfinished lives on a branch and on one machine only.

## Before you create anything

1. Read [REGISTRY.md](../REGISTRY.md). Is there an agent or skill that already does most of the job?
2. If yes, use it, or extend it on a branch (see below). An agent with a slightly different prompt is a copy, not a new agent.
3. Decide where the new one belongs:

| It needs... | Put it in |
|---|---|
| Nothing repo-specific (reviewing, writing, vetting, researching) | Lumbung `agents/` or `skills/` |
| Files, scripts or setup that exist only in one repo | That repo's `.claude/agents/` or `.claude/skills/`, plus a registry row |

When in doubt, start in the repo. Moving it to Lumbung later is easy; pulling a repo's assumptions out of a shared agent is not.

## Develop a new kit agent or skill

```bash
cd /root/lumbung                     # ~/lumbung on Windows
git switch -c feature/report-writer
```

1. Write `agents/report-writer.md` (or `skills/report-writer/SKILL.md`).
   - Frontmatter: `name`, a `description` that says when to use it, and `tools` if it should be limited.
   - Do not hard-code repo paths. If it reads a skill, point at both places it can be: `.agents/skills/<skill>/SKILL.md` in the repo, else `~/.claude/skills/<skill>/SKILL.md`.
2. Add a row to `REGISTRY.md` with status `draft`.
3. Install it on this machine only:
   ```bash
   python3 install.py
   ```
4. Start a new Claude Code session in a repo where you want to try it. Agents are loaded at session start.
5. Use it on real work. Every session start reminds you that Lumbung is in develop mode, so you do not forget the machine is running a branch.
6. Commit as you go. On a Windows machine, push the branch if you want to continue on another machine.

The duplicate guard runs while you write the file. If it blocks you, read which agent it matched before reaching for the override.

## Release it

```bash
# set the registry row to active first
git switch master
git merge --ff-only feature/report-writer      # or merge however you like
git push                                       # if this machine has an origin
python3 install.py
git branch -d feature/report-writer
```

The other machines pick it up at their next session start.

## Drop an idea

```bash
git switch master
python3 install.py          # removes the draft from ~/.claude (it is not in master's manifest)
git branch -D feature/report-writer
```

## Change an existing kit agent or skill

Same branch flow. Never edit `~/.claude/agents/<kit agent>.md` directly: the guard blocks it, and the next sync would overwrite it anyway.

For `security-reviewer`, `slop-reviewer`, `dependency-auditor` and their skills: core-template links to these files. After merging, run `python3 sync-agent-kit.py` in `/root/core-template` and commit the result in `core-backend` and `core-frontend` through their own feature branch flow. Keep the text free of personal setup details: it is published there.

## Repo-bound agents

Develop them inside the repo, following that repo's git flow. Add a registry row with `` repo: `<path>` `` as the location (path as on the VM). The guard reads that path to find the repo's agents on machines where it exists.

**Promote** a repo-bound agent to the kit when `report.py` shows it used in three or more repos, or when you find yourself wanting it somewhere else. Remove the repo-specific parts, move the file into Lumbung on a branch, update the registry row, and delete the repo copy.

## Intentional duplicates

Sometimes a repo really needs its own version of an agent, for example a security reviewer that knows one app's authorization model. Add a frontmatter comment and say why:

```yaml
---
name: seira-security-reviewer
description: ...
# lumbung-override: knows Seira's project/role permission model
---
```

Record it in the registry with the same reason. A repo agent with the same name as a user-level agent wins inside that repo; use a different name unless replacing it there is the point.

## Skills from outside

Treat a third-party skill like a dependency. Read all of it. Check where it comes from and that it does not tell the agent to fetch or run anything. Record its source and content hash in `skills-lock.json` (core-template keeps one for `no-ai-slop`). Then add it on a branch like any other skill.

## Retire an agent or skill

Delete the file on a branch, set the registry status to `retired` (keep the row so the name is not reused by accident), merge, push. `install.py` removes it from every machine at their next sync, because it is no longer in the manifest.

`report.py` lists registry entries that nobody has used in the chosen period; that list is the place to look for candidates.
