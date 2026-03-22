import json
import os
from datetime import datetime, timezone

STATE_FILE = "/root/apex-server-control/data/server_state.json"

DEFAULT_STATE = {
    "mode": "RUN",
    "lock_enabled": False,
    "updated_at": "",
    "updated_by": "system",
    "note": "initial state",
}


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def load_state():
    if not os.path.exists(STATE_FILE):
        return dict(DEFAULT_STATE)

    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)

        result = dict(DEFAULT_STATE)
        result.update(data)
        return result
    except Exception:
        return dict(DEFAULT_STATE)


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    return state


def set_run(by="system", note="system running"):
    state = load_state()
    state["mode"] = "RUN"
    state["lock_enabled"] = False
    state["updated_at"] = _now()
    state["updated_by"] = by
    state["note"] = note
    return save_state(state)


def set_lock(by="system", note="system locked"):
    state = load_state()
    state["mode"] = "LOCK"
    state["lock_enabled"] = True
    state["updated_at"] = _now()
    state["updated_by"] = by
    state["note"] = note
    return save_state(state)


def set_stop(by="system", note="system stopped"):
    state = load_state()
    state["mode"] = "STOP"
    state["updated_at"] = _now()
    state["updated_by"] = by
    state["note"] = note
    return save_state(state)
