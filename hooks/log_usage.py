"""SubagentStart / SubagentStop hook: append one JSON line per event to the local usage log."""

import json
import socket
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def main():
    data = common.read_hook_input()
    event = data.get("hook_event_name", "")
    row = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "host": socket.gethostname().lower(),
        "event": "start" if event == "SubagentStart" else "stop" if event == "SubagentStop" else event,
        "agent": data.get("agent_type") or "general-purpose",
        "agent_id": data.get("agent_id"),
        "session": data.get("session_id"),
        "cwd": data.get("cwd"),
    }
    common.DATA.mkdir(parents=True, exist_ok=True)
    with open(common.USAGE, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
