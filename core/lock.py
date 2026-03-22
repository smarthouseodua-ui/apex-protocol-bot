import os
from datetime import datetime, timezone

LOCK_FILE = "/root/apex-server-control/data/server.lock"


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def is_locked():
    return os.path.exists(LOCK_FILE)


def lock(updated_by="system", reason="manual lock"):
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    with open(LOCK_FILE, "w") as f:
        f.write(f"locked_at={_now()}\n")
        f.write(f"updated_by={updated_by}\n")
        f.write(f"reason={reason}\n")
    return "LOCKED"


def unlock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
        return "UNLOCKED"
    return "ALREADY UNLOCKED"


def read_lock():
    if not os.path.exists(LOCK_FILE):
        return "LOCK: OFF"

    try:
        with open(LOCK_FILE, "r") as f:
            content = f.read().strip()
        return f"LOCK: ON\n{content}"
    except Exception as e:
        return f"LOCK: ERROR {e}"
