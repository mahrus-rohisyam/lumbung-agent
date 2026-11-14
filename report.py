#!/usr/bin/env python3
"""Summarize subagent usage across every machine. Runs on any machine.

Usage: python3 report.py [--days N] [--no-fetch]   (default: 30 days)

Reads this machine's ~/.claude/lumbung/usage.jsonl plus every other machine's usage/<host>.jsonl
from the usage branch (origin/usage after a fetch, or the local usage branch when there is no remote).
"""

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "hooks"))
import common  # noqa: E402


def lines(fetch):
    me = common.config()["host"]
    if common.USAGE.exists():
        yield from common.USAGE.read_text(encoding="utf-8", errors="replace").splitlines()
    remote = common.has_origin()
    if remote and fetch:
        common.git("fetch", "--quiet", "origin", timeout=15)
    ref = None
    for candidate in ([f"origin/{common.USAGE_BRANCH}"] if remote else []) + [common.USAGE_BRANCH]:
        if common.git("rev-parse", "--verify", "--quiet", candidate):
            ref = candidate
            break
    if not ref:
        return
    for path in (common.git("ls-tree", "-r", "--name-only", ref, "usage/") or "").splitlines():
        if Path(path).stem != me:
            yield from (common.git("show", f"{ref}:{path}", timeout=15) or "").splitlines()


def project(cwd):
    parts = [p for p in (cwd or "").replace("\\", "/").split("/") if p]
    return parts[-1] if parts else "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--no-fetch", action="store_true", help="do not fetch the usage branch first")
    a = ap.parse_args()
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - a.days * 86400))

    starts = []
    for line in lines(not a.no_fetch):
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

    print(f"Subagent runs in the last {a.days} days: {len(starts)}\n")
    if starts:
        w = max(len(n) for n in by_agent)
        print(f"{'agent':<{w}}  runs  last used             machines | repos")
        for name, n in by_agent.most_common():
            h = ", ".join(f"{k} {v}" for k, v in hosts[name].most_common())
            p = ", ".join(f"{k} {v}" for k, v in repos[name].most_common(4))
            print(f"{name:<{w}}  {n:>4}  {last[name]}  {h} | {p}")

    registered = [r["name"] for r in common.parse_registry()]
    unused = [n for n in registered if n not in by_agent]
    if unused:
        print(f"\nIn REGISTRY.md but unused for {a.days} days: {', '.join(unused)}")
    builtin = {"general-purpose", "Explore", "Plan", "claude-code-guide", "statusline-setup", "fork", "claude"}
    unlisted = [n for n in by_agent if n not in registered and n not in builtin and len(repos[n]) >= 2]
    if unlisted:
        print(f"Used in 2+ repos but not in REGISTRY.md: {', '.join(unlisted)}")
    spread = [n for n in by_agent if len(repos[n]) >= 3]
    if spread:
        print(f"Used in 3+ repos (move to the kit if repo-bound): {', '.join(spread)}")


if __name__ == "__main__":
    main()
