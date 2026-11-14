"""SessionStart hook: update the kit from its git remote, reinstall if it changed, publish usage.

Never blocks a session: git runs with short timeouts and never prompts; any failure is silent.
Prints a line (added to the session context) only when the kit was updated or is in develop mode.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def publish_usage(host, remote):
    """Write this machine's log to usage/<host>.jsonl on the usage branch without touching the checkout."""
    if not common.USAGE.exists():
        return
    ref = f"refs/remotes/origin/{common.USAGE_BRANCH}" if remote else f"refs/heads/{common.USAGE_BRANCH}"
    parent = common.git("rev-parse", "--verify", "--quiet", ref)
    if remote and not parent:
        parent = common.git("rev-parse", "--verify", "--quiet", f"refs/heads/{common.USAGE_BRANCH}")
    blob = common.git("hash-object", "-w", str(common.USAGE))
    path = f"usage/{host}.jsonl"
    if not blob or (parent and common.git("rev-parse", f"{parent}:{path}") == blob):
        return
    fd, index = tempfile.mkstemp(prefix="lumbung-index-")
    os.close(fd)
    os.unlink(index)
    env = {"GIT_INDEX_FILE": index, "GIT_AUTHOR_NAME": f"lumbung@{host}", "GIT_AUTHOR_EMAIL": "lumbung@localhost",
           "GIT_COMMITTER_NAME": f"lumbung@{host}", "GIT_COMMITTER_EMAIL": "lumbung@localhost"}
    try:
        common.git("read-tree", parent if parent else "--empty", env=env)
        common.git("update-index", "--add", "--cacheinfo", f"100644,{blob},{path}", env=env)
        tree = common.git("write-tree", env=env)
        if not tree:
            return
        commit = common.git("commit-tree", tree, *(["-p", parent] if parent else []), "-m", f"usage: {host}", env=env)
        if not commit or common.git("update-ref", f"refs/heads/{common.USAGE_BRANCH}", commit) is None:
            return
        if remote:  # rejected (someone pushed first) -> rebuilt on the new tip next session
            common.git("push", "--quiet", "origin", f"refs/heads/{common.USAGE_BRANCH}", timeout=8)
    finally:
        if os.path.exists(index):
            os.unlink(index)


def main():
    common.read_hook_input()
    cfg = common.config()
    remote = common.has_origin()
    branch = common.git("rev-parse", "--abbrev-ref", "HEAD")
    before = common.git("rev-parse", "HEAD")
    notes = []

    if remote:
        common.git("fetch", "--quiet", "origin", timeout=8)
    if branch == common.MAIN:
        if remote:
            common.git("merge", "--ff-only", "--quiet", f"origin/{common.MAIN}")
    elif branch:
        notes.append(f"Lumbung is on branch '{branch}' (develop mode): not updating from the remote. Run install.py "
                     f"after each change; switch back to '{common.MAIN}' and run install.py when done.")
    after = common.git("rev-parse", "HEAD")

    if after and after != cfg.get("installed_commit"):
        r = subprocess.run([sys.executable, str(common.KIT / "install.py"), "--quiet"], capture_output=True, text=True)
        if r.returncode == 0 and before and before != after and branch == common.MAIN:
            log = common.git("log", "--format=%s", f"{before}..{after}") or ""
            notes.append(f"Lumbung updated to {after[:7]}: " + "; ".join(log.splitlines()[:5]))

    publish_usage(cfg["host"], remote)
    if notes:
        print("\n".join(notes))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # a broken sync must never break a session
        pass
