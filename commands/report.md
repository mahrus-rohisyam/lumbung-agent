---
description: Show which subagents ran on this machine, how often and in which repos
argument-hint: "[days]"
allowed-tools: Bash
---

Run this with the Bash tool. Use `python3`; if that is missing or fails, use `python`, then `py -3`. Pass `--days $ARGUMENTS` only when an argument was given.

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/report.py" --data "${CLAUDE_PLUGIN_DATA}"
```

Show the output as is. Then add at most three short observations: agents that are never used, repo-bound agents used in many repos (candidates to move into Lumbung), and agents missing from REGISTRY.md. Do not change any file.
