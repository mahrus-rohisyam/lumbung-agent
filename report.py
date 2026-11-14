#!/usr/bin/env python3
"""Summarize subagent usage from every machine. Run on the VM (the hub).

Usage: python3 report.py [--days N]   (default: 30)

Reads ~/.claude/agent-harness/usage.jsonl (this machine) and inbox/*.jsonl (shipped by the others).
"""

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "hooks"))
import common  # noqa: E402


def rows():
    files = [common.USAGE] + sorted(common.INBOX.glob("*.jsonl")) if common.INBOX.is_dir() else [common.USAGE]
    for f in files:
        if not f.exists():
            continue
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                yield json.loads(line)
            except ValueError:
                continue


def project(cwd):
    if not cwd:
        return "?"
    parts = [p for p in cwd.replace("\\", "/").split("/") if p]
    return parts[-1] if parts else cwd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    a = ap.parse_args()
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - a.days * 86400))

    starts = [r for r in rows() if r.get("event") == "start" and r.get("ts", "") >= since]
    by_agent = Counter(r["agent"] for r in starts)
    hosts, repos, last = defaultdict(Counter), defaultdict(Counter), {}
    for r in starts:
        hosts[r["agent"]][r.get("host", "?")] += 1
        repos[r["agent"]][project(r.get("cwd"))] += 1
        last[r["agent"]] = max(last.get(r["agent"], ""), r["ts"])

    print(f"Subagent runs in the last {a.days} days: {len(starts)}\n")
    if starts:
        w = max(len(n) for n in by_agent)
        print(f"{'agent':<{w}}  runs  last used             hosts / repos")
        for name, n in by_agent.most_common():
            h = ", ".join(f"{k} {v}" for k, v in hosts[name].most_common())
            p = ", ".join(f"{k} {v}" for k, v in repos[name].most_common(4))
            print(f"{name:<{w}}  {n:>4}  {last[name]}  {h} | {p}")

    registered = [r["name"] for r in common.parse_registry()]
    unused = [n for n in registered if n not in by_agent]
    if unused:
        print(f"\nIn REGISTRY.md but not used in {a.days} days: {', '.join(unused)}")
    many = [n for n in by_agent if n not in registered and n != "general-purpose" and len(repos[n]) >= 2]
    if many:
        print(f"Not in REGISTRY.md: {', '.join(many)}")
    spread = [n for n in by_agent if len(repos[n]) >= 3]
    if spread:
        print(f"Used in 3+ repos (worth having in the kit if repo-bound): {', '.join(spread)}")


if __name__ == "__main__":
    main()
