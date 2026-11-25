## Subagents and skills (Lumbung plugin)

The `lumbung` plugin supplies shared subagents, skills, and rules across machines. Its source is your `lumbung-agent` repository clone (for example `~/lumbung-agent`). `REGISTRY.md` in that repo lists every subagent and skill, what it does, and where it lives; `docs/workflow.md` is the full procedure.

- Before creating a subagent or skill, read `REGISTRY.md`. If one already does the job, use it or extend it. Do not create a near copy in a repo.
- A subagent or skill that is useful beyond one repo goes in the `lumbung-agent` clone (`agents/`, `skills/`), on a `feature/<name>` branch, never straight on `master`. Merge to `master` and push to share it across machines.
- A repo-bound subagent (needs that repo's files) stays in the repo (`.claude/agents/` or `.agents/agents/`), and still gets a row in `REGISTRY.md`.
- Add or update the `REGISTRY.md` row in the same change (status `draft` until merged, then `active`).
- Never edit installed plugin cache copies under `~/.claude/plugins/` (Claude Code); edit the source clone instead.
- A `PreToolUse` hook blocks agent files that duplicate an existing one. If a separate version is really needed, add `# lumbung-override: <reason>` to its frontmatter and record the reason in `REGISTRY.md`.
- In Claude Code, `/lumbung:report` shows which subagents ran on this machine, how often, and in which repos.
