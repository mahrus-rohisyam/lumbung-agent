"""Shared paths and helpers for Lumbung hooks and scripts. Standard library only."""

import json
import os
import re
from pathlib import Path

PLUGIN = "lumbung"
KIT = Path(__file__).resolve().parent.parent  # plugin root: the installed copy, or a --plugin-dir clone
CLAUDE = Path.home() / ".claude"
# Claude Code exports CLAUDE_PLUGIN_DATA to hooks; it survives plugin updates.
DATA = Path(
    os.environ.get("CLAUDE_PLUGIN_DATA")
    or os.environ.get("PLUGIN_DATA")
    or CLAUDE / "plugins" / "data" / "lumbung-lumbung-agent"
)
USAGE = DATA / "usage.jsonl"
OVERRIDE = "lumbung-override"


def read_hook_input():
    import sys

    try:
        return json.load(sys.stdin)
    except ValueError:
        return {}


def plugin_name(root):
    """Manifest name of the plugin at root, or None when root is not a plugin."""
    root = Path(root)
    for rel in (
        Path("plugin.json"),
        Path(".antigravity-plugin") / "plugin.json",
        Path(".claude-plugin") / "plugin.json",
    ):
        try:
            return json.loads((root / rel).read_text(encoding="utf-8")).get("name")
        except (OSError, ValueError):
            continue
    return None


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
    """The repo path in a registry location like 'repo: `~/projects/my-app`', or None."""
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
