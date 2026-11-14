## Subagents and skills (Lumbung)

Shared subagents and skills for every machine live in the Lumbung repo (VM: `/root/lumbung`, laptop/PC: `~/lumbung`). Its `REGISTRY.md` lists every subagent and skill, what it does and where it lives; `docs/workflow.md` is the full procedure.

- Before creating a subagent or skill, read `REGISTRY.md`. If one does the job, use it or extend it. Do not create a near copy in a repo.
- A subagent or skill that is useful beyond one repo goes in Lumbung (`agents/`, `skills/`), on a `feature/<name>` branch, never straight on `master`. Run `install.py` to try it on this machine; merge to `master` and push to share it.
- A repo-bound subagent (needs that repo's files) stays in the repo, but still gets a row in `REGISTRY.md`.
- Add or update the `REGISTRY.md` row in the same change (status `draft` until merged, then `active`).
- Never edit the installed copies in `~/.claude/agents` or `~/.claude/skills` that come from Lumbung; edit the repo and run `install.py`.
- A hook blocks agents that duplicate an existing one. If a separate version is really needed, add `# lumbung-override: <reason>` to its frontmatter and record the reason in `REGISTRY.md`.
- `python3 report.py` in the Lumbung repo shows which subagents run, on which machine and in which repo.
