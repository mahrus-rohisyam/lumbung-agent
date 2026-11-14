"""Shared paths and helpers for Lumbung hooks and scripts. Standard library only."""

import json
import os
import re
import socket
import subprocess
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
CLAUDE = Path.home() / ".claude"
STATE = CLAUDE / "lumbung"
CONFIG = STATE / "config.json"
MANIFEST = STATE / "manifest.json"
USAGE = STATE / "usage.jsonl"

MAIN = "master"  # the branch every machine runs
USAGE_BRANCH = "usage"  # usage logs, one file per machine: usage/<host>.jsonl
OVERRIDE = "lumbung-override"


def load_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def config():
    cfg = load_json(CONFIG, {})
    cfg.setdefault("host", socket.gethostname().lower())
    return cfg


def git(*args, timeout=5, env=None):
    """Run git in the kit; returns stdout, or None on any failure. Never prompts."""
    e = dict(os.environ, GIT_TERMINAL_PROMPT="0", **(env or {}))
    try:
        r = subprocess.run(["git", "-C", str(KIT), *args], capture_output=True, text=True, timeout=timeout,
                           env=e, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def has_origin():
    return "origin" in (git("remote") or "").split()


def read_hook_input():
    import sys

    try:
        return json.load(sys.stdin)
    except ValueError:
        return {}


def parse_registry():
    """Rows of the Agents table in REGISTRY.md as dicts: name, purpose, location, status."""
    rows, in_agents = [], False
    for line in (KIT / "REGISTRY.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_agents = line.strip().lower() == "## agents"
            continue
        if not in_agents or not line.startswith("|") or set(line) <= set("|-: "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0].lower() == "name":
            continue
        rows.append({"name": cells[0].strip("`"), "purpose": cells[1], "location": cells[2], "status": cells[3]})
    return rows


def location_path(row):
    """The repo path in a registry location like 'repo: `/root/marketing`', or None."""
    m = re.search(r"`([^`]+)`", row["location"])
    return Path(m.group(1)).expanduser() if m else None


def frontmatter(text):
    """Very small YAML-frontmatter reader: top-level `key: value` lines and `# comments`."""
    out, comments = {}, []
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return out, comments
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.lstrip().startswith("#"):
            comments.append(line.lstrip()[1:].strip())
        elif ":" in line and not line.startswith((" ", "\t")):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip("'\"")
    return out, comments
