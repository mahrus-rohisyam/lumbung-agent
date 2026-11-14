# Working with agents and skills

The rule behind everything here: **`master` is what every machine runs.** Every push to `master` reaches every machine through auto-update. Anything unfinished lives on a branch and runs only in sessions you start for it.

## Before you create anything

1. Read [REGISTRY.md](../REGISTRY.md). Is there an agent or skill that already does most of the job?
2. If yes, use it, or extend it on a branch (see below). An agent with a slightly different prompt is a copy, not a new agent.
3. Decide where the new one belongs:

| It needs... | Put it in |
|---|---|
| Nothing repo-specific (reviewing, writing, vetting, researching) | This repo's `agents/` or `skills/` |
| Files, scripts or setup that exist only in one repo | That repo's `.claude/agents/` or `.claude/skills/`, plus a registry row here |

When in doubt, start in the repo. Moving it into Lumbung later is easy; pulling a repo's assumptions out of a shared agent is not.

## Get a clone

You only need one on a machine where you develop. VM: `/root/lumbung-agent`. Windows:

```powershell
git clone https://github.com/mahrus-rohisyam/lumbung-agent $HOME\lumbung-agent
```

## Develop a new agent or skill

```bash
cd ~/lumbung-agent                        # /root/lumbung-agent on the VM
git switch -c feature/report-writer
```

1. Write `agents/report-writer.md`, or `skills/report-writer/SKILL.md`.
   - Frontmatter: `name`, a `description` that says when to use it, and `tools` if it should be limited.
   - Do not hard-code repo paths. If it reads one of the kit's skills, point at it by name (the `secure-coding` skill), so it works both from the plugin and from a repo that has its own copy.
2. Add a row to `REGISTRY.md` with status `draft`.
3. Try it in a repo where it is useful, loading your clone instead of the installed plugin:
   ```bash
   cd /path/to/some/repo
   claude --plugin-dir ~/lumbung-agent
   ```
   For that session the clone replaces the installed `lumbung` plugin, so you see your branch, new agent included. Other sessions and other machines keep the released version.
4. Use it on real work. Edit, then start a new `--plugin-dir` session, or run `/reload-plugins`, to load the change.
5. Commit as you go. Push the branch if you want to continue on another machine.

The duplicate guard runs while you write the file. If it blocks you, read which agent it matched before reaching for the override.

**On the VM while it installs from the local path:** that install loads the clone in place, so every session on the VM runs whatever branch is checked out. Switch back to `master` when you stop working on the branch.

## Release it

```bash
# set the registry row to active first
git switch master
git merge --ff-only feature/report-writer
git push
git branch -d feature/report-writer
```

Machines with auto-update pick it up after their next session starts. To get it right away: `/plugin` → **Marketplaces** → `lumbung-agent` → **Update marketplace**, then `/reload-plugins`.

## Drop an idea

```bash
git switch master
git branch -D feature/report-writer
```

Nothing was ever installed, so there is nothing to clean up.

## Change an existing agent or skill

Same branch flow. Never edit the copy under `~/.claude/plugins/`. The guard blocks it, and the next update replaces it anyway.

For `security-reviewer`, `slop-reviewer`, `dependency-auditor` and their skills: core-template links to these files. After merging, run `python3 sync-agent-kit.py` in `/root/core-template` and commit the result in `core-backend` and `core-frontend` through their own feature branch flow. Keep the text free of personal setup details, because it is published there.

## Repo-bound agents

Develop them inside the repo, following that repo's git flow. Add a registry row here with `` repo: `<path>` `` as the location (path as on the VM). The guard reads that path to find the repo's agents on machines where it exists.

**Promote** a repo-bound agent into Lumbung when `/lumbung:report` shows it used in three or more repos, or when you find yourself wanting it somewhere else. Remove the repo-specific parts, move the file into this repo on a branch, update the registry row, and delete the repo copy.

## Intentional duplicates

Sometimes a repo needs its own version of an agent, for example a security reviewer that knows one app's authorization model. Add a frontmatter comment that says why:

```yaml
---
name: seira-security-reviewer
description: ...
# lumbung-override: knows Seira's project/role permission model
---
```

Record it in the registry with the same reason.

## Skills from outside

Treat a third-party skill like a dependency. Read all of it. Check where it comes from and that it does not tell the agent to fetch or run anything. Record its source and content hash (core-template's `skills-lock.json` keeps the one for `no-ai-slop`). Then add it on a branch like any other skill.

A third-party *plugin* can be installed directly from its own marketplace instead. It does not need to go through Lumbung, but it does need a registry row, so the guard and the next person know it exists.

## Retire an agent or skill

On a branch, delete the file and set the registry status to `retired`. Keep the row so the name is not reused by accident. Merge and push; the next update removes it from every machine.

`/lumbung:report` lists registry entries nobody has used in the chosen period: the place to look for candidates.
