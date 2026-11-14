## Subagents and skills (Lumbung plugin)

The `lumbung` plugin supplies the shared subagents and skills on every machine (they appear as `lumbung:<name>`). Its source is the lumbung-agent repo; my clone is `/root/lumbung-agent` on the VM and `~/lumbung-agent` on the laptop/PC. `REGISTRY.md` in that repo lists every subagent and skill, what it does and where it lives; `docs/workflow.md` is the full procedure.

- Before creating a subagent or skill, read `REGISTRY.md`. If one does the job, use it or extend it. Do not create a near copy in a repo.
- A subagent or skill that is useful beyond one repo goes in the lumbung-agent clone (`agents/`, `skills/`), on a `feature/<name>` branch, never straight on `master`. Try it with `claude --plugin-dir <clone>`; merge to `master` and push to share it.
- A repo-bound subagent (needs that repo's files) stays in the repo, but still gets a row in `REGISTRY.md`.
- Add or update the `REGISTRY.md` row in the same change (status `draft` until merged, then `active`).
- Never edit plugin copies under `~/.claude/plugins/`; Claude Code replaces them on every update.
- A hook blocks agents that duplicate an existing one. If a separate version is really needed, add `# lumbung-override: <reason>` to its frontmatter and record the reason in `REGISTRY.md`.
- `/lumbung:report` shows which subagents ran on this machine, how often and in which repos.
