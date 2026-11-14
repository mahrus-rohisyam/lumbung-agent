"""SessionStart hook: pull the kit from the hub, reinstall if it changed, ship usage logs.

Never blocks a session: every network step has a short timeout and failures are silent.
Prints one line (added to the session context) only when the kit was updated.
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=4"]


def ship_usage(hub):
    if not common.USAGE.exists():
        return
    try:
        offset = int(common.SHIPPED.read_text().strip() or 0)
    except (OSError, ValueError):
        offset = 0
    data = common.USAGE.read_bytes()
    if offset > len(data):  # log was rotated or reset
        offset = 0
    chunk = data[offset:]
    if not chunk:
        return
    host = common.config()["host"]
    remote = f"mkdir -p ~/.claude/agent-harness/inbox && cat >> ~/.claude/agent-harness/inbox/{host}.jsonl"
    try:
        r = subprocess.run(SSH + [hub, remote], input=chunk, capture_output=True, timeout=8)
    except (OSError, subprocess.TimeoutExpired):
        return
    if r.returncode == 0:
        common.SHIPPED.write_text(str(offset + len(chunk)))


def main():
    common.read_hook_input()
    cfg = common.config()
    before = common.git("rev-parse", "HEAD")
    if cfg.get("hub"):
        common.git("-c", "core.sshCommand=" + " ".join(SSH), "pull", "--ff-only", "--quiet", timeout=10)
    after = common.git("rev-parse", "HEAD")

    if after and after != cfg.get("installed_commit"):
        r = subprocess.run([sys.executable, str(common.KIT / "install.py"), "--quiet"], capture_output=True, text=True)
        if r.returncode == 0 and before != after:
            log = common.git("log", "--format=%s", f"{before}..{after}") or ""
            print(f"agent-harness updated to {after[:7]}: " + "; ".join(log.splitlines()[:5]))

    if cfg.get("hub"):
        ship_usage(cfg["hub"])


if __name__ == "__main__":
    try:
        main()
    except Exception:  # a broken sync must never break a session
        pass
