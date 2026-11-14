#!/usr/bin/env python3
"""Install Lumbung into ~/.claude on this machine (Linux or Windows). Safe to re-run.

Usage:
  python3 install.py                 # install or refresh from the current checkout
  python3 install.py --host <name>   # set the machine name used in usage logs (default: hostname)
  python3 install.py --uninstall     # remove everything this script added (usage log is kept)

What it touches:
  ~/.claude/agents/<kit agents>, ~/.claude/skills/<kit skills>  (only names listed in the manifest)
  ~/.claude/CLAUDE.md   block between BEGIN/END lumbung markers
  ~/.claude/settings.json  hook entries whose args point into this kit; other hooks are left alone
  ~/.claude/lumbung/  config, manifest, usage log, settings backup
"""

import argparse
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "hooks"))
import common  # noqa: E402

BEGIN, END = "<!-- BEGIN lumbung -->", "<!-- END lumbung -->"


def hook(script, timeout):
    return {
        "type": "command",
        "command": Path(sys.executable).as_posix(),
        "args": [(common.KIT / "hooks" / script).as_posix()],
        "timeout": timeout,
    }


HOOKS = {
    "SessionStart": [{"matcher": "startup", "hooks": [hook("sync.py", 30)]}],
    "PreToolUse": [{"matcher": "Write|Edit|MultiEdit", "hooks": [hook("guard_agent.py", 10)]}],
    "SubagentStart": [{"matcher": "*", "hooks": [hook("log_usage.py", 5)]}],
    "SubagentStop": [{"matcher": "*", "hooks": [hook("log_usage.py", 5)]}],
}


def ours(entry):
    kit = common.KIT.as_posix()
    return any(kit in " ".join([h.get("command", "")] + list(h.get("args", []))) for h in entry.get("hooks", []))


def merge_settings(install):
    path = common.CLAUDE / "settings.json"
    settings = common.load_json(path, {})
    if path.exists() and not (common.STATE / "settings.json.before-lumbung").exists():
        common.STATE.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, common.STATE / "settings.json.before-lumbung")
    hooks = settings.setdefault("hooks", {})
    for event in list(hooks):
        hooks[event] = [e for e in hooks[event] if not ours(e)]
    if install:
        for event, entries in HOOKS.items():
            hooks.setdefault(event, []).extend(entries)
    for event in [e for e, v in hooks.items() if not v]:
        del hooks[event]
    if not hooks:
        del settings["hooks"]
    common.save_json(path, settings)


def merge_rules(install):
    path = common.CLAUDE / "CLAUDE.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if BEGIN in text and END in text:
        start, end = text.index(BEGIN), text.index(END) + len(END)
        text = (text[:start].rstrip() + "\n\n" + text[end:].lstrip()).strip() + "\n"
    if install:
        block = (common.KIT / "rules" / "CLAUDE.md").read_text(encoding="utf-8").strip()
        text = (text.rstrip() + "\n\n" if text.strip() else "") + f"{BEGIN}\n{block}\n{END}\n"
    if text.strip():
        path.write_text(text, encoding="utf-8")
    elif path.exists():
        path.unlink()


def remove(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def sync_files(install):
    old = common.load_json(common.MANIFEST, {"agents": [], "skills": []})
    new = {"agents": [], "skills": []}
    if install:
        new["agents"] = sorted(p.name for p in (common.KIT / "agents").glob("*.md"))
        new["skills"] = sorted(p.name for p in (common.KIT / "skills").iterdir() if (p / "SKILL.md").exists())
    for kind in ("agents", "skills"):
        dest = common.CLAUDE / kind
        for name in set(old[kind]) - set(new[kind]):
            remove(dest / name)
        dest.mkdir(parents=True, exist_ok=True)
        for name in new[kind]:
            if (dest / name).exists() and name not in old[kind]:
                print(f"  ! {kind}/{name} already exists and is not from the kit; replacing it")
            remove(dest / name)
            src = common.KIT / kind / name
            if src.is_dir():
                shutil.copytree(src, dest / name)
            else:
                shutil.copy2(src, dest / name)
    common.save_json(common.MANIFEST, new)
    return new


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", help="machine name in usage logs (default: hostname)")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    cfg = common.config()
    if a.host:
        cfg["host"] = a.host
    install = not a.uninstall

    files = sync_files(install)
    merge_rules(install)
    merge_settings(install)
    cfg["installed_commit"] = common.git("rev-parse", "HEAD") if install else None
    cfg["installed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    common.save_json(common.CONFIG, cfg)

    if not a.quiet:
        if install:
            branch = common.git("rev-parse", "--abbrev-ref", "HEAD") or "?"
            remote = common.git("remote", "get-url", "origin") or "no remote"
            print(f"Lumbung installed on {cfg['host']} (branch {branch}, origin: {remote})")
            print(f"  agents: {', '.join(files['agents'])}")
            print(f"  skills: {', '.join(files['skills'])}")
        else:
            print("Lumbung removed (usage log kept in ~/.claude/lumbung)")


if __name__ == "__main__":
    main()
