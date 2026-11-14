## Subagents and skills (agent-harness)

The shared kit for every machine lives in the agent-harness repo (VM: `/root/agent-harness`, laptop/PC: `~/agent-harness`). Its `REGISTRY.md` lists every subagent and skill: what it does and where it lives.

- Before creating a subagent or skill, read `REGISTRY.md`. If one does the job, use it or extend it. Do not create a near copy in a repo.
- A subagent that is useful beyond one repo goes in the kit's `agents/` (skills in `skills/`), not in the repo's `.claude/agents/`. Then run `install.py` and commit in the kit.
- A repo-bound subagent (needs that repo's files) stays in the repo, but still gets a row in `REGISTRY.md` with its location.
- Add or update the `REGISTRY.md` row in the same change that adds the subagent or skill.
- Never edit the installed copies in `~/.claude/agents` or `~/.claude/skills` that come from the kit; edit the kit and run `install.py`.
- A hook blocks agents that duplicate an existing one. If a separate version is really needed, add `# harness-override: <reason>` to its frontmatter and record the reason in `REGISTRY.md`.
- Usage: `python3 /root/agent-harness/report.py` on the VM shows which subagents run, where and how often.
