"""PreToolUse hook: stop redundant subagents before they are written.

Supports both Claude Code (Write|Edit|MultiEdit) and Antigravity
(write_file|edit_file|write_to_file|replace_file_content|multi_replace_file_content).

Only acts on agent files: */.claude/agents/*.md, */.agents/agents/*.md,
*/.agent/agents/*.md, or agents/*.md inside a plugin (such as a Lumbung clone).
  - Any write into ~/.claude/plugins/cache or /marketplaces (managed by Claude Code) -> deny (edit the clone).
  - New agent whose name is already in REGISTRY.md or used by another agent file -> deny.
  - New agent whose description overlaps strongly with an existing agent -> deny.
  - New agent not in REGISTRY.md -> allow, with a reminder to register it.
A frontmatter comment `# lumbung-override: <reason>` lets an intentional duplicate through
(e.g. a repo-specific version); the reminder then asks for the reason in REGISTRY.md.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

STOP = set(
    """the and for with that this from into your you use used when after before any all are can
    not but its it's each per via only also than then them they their there what which who will
    agent agents subagent skill skills against read-only readonly given using make makes""".split()
)
THRESHOLD = 0.5  # share of the smaller token set
MIN_SHARED = 3
SUPPORTED_TOOLS = {
    "Write",
    "Edit",
    "MultiEdit",
    "write_file",
    "edit_file",
    "write_to_file",
    "replace_file_content",
    "multi_replace_file_content",
}


def tokens(text):
    words = re.findall(r"[a-z][a-z0-9]{2,}", text.lower())
    return {w[:6] for w in words if w not in STOP}


def deny(reason, mode="claude"):
    if mode == "antigravity":
        print(json.dumps({"decision": "deny", "reason": reason}))
    else:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": reason,
                    }
                }
            )
        )
    sys.exit(0)


def note(text, mode="claude"):
    if mode == "antigravity":
        print(json.dumps({"decision": "allow", "reason": text}))
    else:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": text}}))
    sys.exit(0)


def is_agent_file(p):
    parts = [x.lower() for x in p.parts]
    if p.suffix.lower() != ".md" or len(parts) < 2 or parts[-2] != "agents":
        return False
    return (len(parts) >= 3 and parts[-3] in (".claude", ".agents", ".agent")) or (
        common.plugin_name(p.parent.parent) is not None
    )


def new_content(tool, inp, path):
    if tool in ("Write", "write_file", "write_to_file"):
        return inp.get("content") or inp.get("Content") or inp.get("CodeContent") or ""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if tool == "edit_file":
        return text.replace(inp.get("Target", ""), inp.get("Replacement", ""))
    if tool in ("replace_file_content", "multi_replace_file_content"):
        chunks = inp.get("ReplacementChunks") or ([inp] if "TargetContent" in inp else [])
        for c in chunks:
            old, new = c.get("TargetContent", ""), c.get("ReplacementContent", "")
            text = text.replace(old, new) if c.get("AllowMultiple") else text.replace(old, new, 1)
        return text
    edits = inp.get("edits") if tool == "MultiEdit" else [inp]
    for e in edits or []:
        old, new = e.get("old_string", ""), e.get("new_string", "")
        text = text.replace(old, new) if e.get("replace_all") else text.replace(old, new, 1)
    return text


def registered_here(row, target):
    """True when the registry row says the agent lives where it is being written (it was registered first)."""
    loc = row["location"].lower()
    if loc.startswith("kit"):
        return target.parent.name == "agents" and common.plugin_name(target.parent.parent) == common.PLUGIN
    repo = common.location_path(row)
    if repo:
        try:
            target.relative_to(repo.resolve())
            return True
        except ValueError:
            return False
    return False


def known_agents(exclude):
    """name -> (description, where) for every agent file visible on this machine."""
    found = {}
    dirs = [common.KIT / "agents", common.CLAUDE / "agents"]
    for row in common.parse_registry():
        repo = common.location_path(row)
        if repo:
            dirs.extend([repo / ".claude" / "agents", repo / ".agents" / "agents", repo / ".agent" / "agents"])
    for d in dirs:
        for f in sorted(d.glob("*.md")) if d.is_dir() else []:
            if f.resolve() == exclude:
                continue
            meta, _ = common.frontmatter(f.read_text(encoding="utf-8", errors="replace"))
            name = meta.get("name") or f.stem
            found.setdefault(name, (meta.get("description", ""), str(f)))
    return found


def parse_hook_request(data):
    if "toolCall" in data:
        tc = data.get("toolCall") or {}
        inp = tc.get("args") or {}
        raw = inp.get("Path") or inp.get("TargetFile") or inp.get("file_path")
        return "antigravity", tc.get("name", ""), inp, raw
    inp = data.get("tool_input") or {}
    return "claude", data.get("tool_name", ""), inp, inp.get("file_path")


def main():
    data = common.read_hook_input()
    mode, tool, inp, raw = parse_hook_request(data)
    if tool not in SUPPORTED_TOOLS or not raw:
        return
    path = Path(raw.replace("\\", "/")).expanduser()
    if not path.is_absolute():
        path = Path(data.get("cwd") or ".") / path
    resolved = path.resolve()
    for managed in ("cache", "marketplaces"):
        try:
            resolved.relative_to((common.CLAUDE / "plugins" / managed).resolve())
        except ValueError:
            continue
        deny(
            f"{resolved} is a plugin copy managed by Claude Code and is replaced on every update. Edit the "
            f"file in the plugin's own clone instead; for Lumbung, on a feature/* branch (see docs/workflow.md).",
            mode,
        )
    if not is_agent_file(path):
        return

    content = new_content(tool, inp, resolved)
    if content is None:
        return
    meta, comments = common.frontmatter(content)
    name = meta.get("name") or path.stem
    override = next((c.split(":", 1)[1].strip() for c in comments if c.lower().startswith(common.OVERRIDE + ":")), None)

    old_name = None
    if resolved.exists():
        old_name = common.frontmatter(resolved.read_text(encoding="utf-8", errors="replace"))[0].get("name") or path.stem
    if old_name == name:
        return  # updating an existing agent in place

    registry = {r["name"]: r for r in common.parse_registry()}
    others = known_agents(resolved)
    if not override:
        if name in others:
            deny(
                f"An agent named '{name}' already exists at {others[name][1]}. Use or extend it. If a separate "
                f"version is really needed, add '# lumbung-override: <reason>' to the frontmatter.",
                mode,
            )
        if name in registry and not registered_here(registry[name], resolved):
            r = registry[name]
            deny(
                f"'{name}' is already in REGISTRY.md ({r['location']}): {r['purpose']}. Use or extend it, or add "
                f"'# lumbung-override: <reason>'.",
                mode,
            )
        mine = tokens(name.replace("-", " ") + " " + meta.get("description", ""))
        candidates = [(n, d + " " + registry.get(n, {}).get("purpose", ""), w) for n, (d, w) in others.items()]
        candidates += [(n, r["purpose"], r["location"]) for n, r in registry.items() if n not in others and n != name]
        best = None
        for n, desc, where in candidates:
            theirs = tokens(n.replace("-", " ") + " " + desc)
            shared = mine & theirs
            if mine and theirs and len(shared) >= MIN_SHARED:
                score = len(shared) / min(len(mine), len(theirs))
                if score >= THRESHOLD and (best is None or score > best[0]):
                    best = (score, n, where, sorted(shared))
        if best:
            deny(
                f"New agent '{name}' overlaps with existing agent '{best[1]}' ({best[2]}); shared terms: "
                f"{', '.join(best[3])}. Use or extend '{best[1]}'. If it is really different, add "
                f"'# lumbung-override: <reason>' to the frontmatter.",
                mode,
            )

    if name not in registry:
        why = f" with the override reason ({override})" if override else ""
        note(
            f"Agent '{name}' is not in Lumbung's REGISTRY.md. Add a row for it{why} in the Agents table of your "
            f"Lumbung clone. If it is useful beyond this repo, create it in the clone's agents/ on a feature/* "
            f"branch instead (see docs/workflow.md in the Lumbung repo).",
            mode,
        )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        pass
