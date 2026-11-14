#!/usr/bin/env python3
"""Summarize subagent usage on this machine.

Usage: report.py [--days N] [--data DIR] [LOG ...]
  --days N    period to cover (default 30)
  --data DIR  the plugin's data directory (default: $CLAUDE_PLUGIN_DATA, else ~/.claude/plugins/data/lumbung-lumbung-agent)
  LOG ...     extra usage.jsonl files, e.g. copied from another machine, to include in the summary
"""

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
import common  # noqa: E402

BUILTIN = {"general-purpose", "Explore", "Plan", "claude-code-guide", "statusline-setup", "fork", "claude"}


def project(cwd):
    parts = [p for p in (cwd or "").replace("\\", "/").split("/") if p]
    return parts[-1] if parts else "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--data", type=Path, default=common.DATA)
    ap.add_argument("logs", nargs="*", type=Path)
    a = ap.parse_args()
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - a.days * 86400))

    starts = []
    for f in [a.data / "usage.jsonl", *a.logs]:
        if not f.exists():
            continue
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("event") == "start" and r.get("ts", "") >= since:
                starts.append(r)

    by_agent = Counter(r["agent"] for r in starts)
    hosts, repos, last = defaultdict(Counter), defaultdict(Counter), {}
    for r in starts:
        hosts[r["agent"]][r.get("host", "?")] += 1
        repos[r["agent"]][project(r.get("cwd"))] += 1
        last[r["agent"]] = max(last.get(r["agent"], ""), r["ts"])

    print(f"Subagent runs in the last {a.days} days: {len(starts)}  (log: {a.data / 'usage.jsonl'})\n")
    if starts:
        w = max(len(n) for n in by_agent)
        print(f"{'agent':<{w}}  runs  last used             machines | repos")
        for name, n in by_agent.most_common():
            h = ", ".join(f"{k} {v}" for k, v in hosts[name].most_common())
            p = ", ".join(f"{k} {v}" for k, v in repos[name].most_common(4))
            print(f"{name:<{w}}  {n:>4}  {last[name]}  {h} | {p}")

    def bare(n):
        return n.split(":", 1)[1] if n.startswith(common.PLUGIN + ":") else n

    used = {bare(n) for n in by_agent}
    registered = [r["name"] for r in common.parse_registry()]
    unused = [n for n in registered if n not in used]
    if unused:
        print(f"\nIn REGISTRY.md but unused for {a.days} days: {', '.join(unused)}")
    unlisted = [n for n in by_agent if bare(n) not in registered and n not in BUILTIN and len(repos[n]) >= 2]
    if unlisted:
        print(f"Used in 2+ repos but not in REGISTRY.md: {', '.join(unlisted)}")
    spread = [n for n in by_agent if n not in BUILTIN and len(repos[n]) >= 3]
    if spread:
        print(f"Used in 3+ repos (move to Lumbung if repo-bound): {', '.join(spread)}")


if __name__ == "__main__":
    main()
