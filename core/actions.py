from core.state import set_run, set_lock, set_stop
from core.lock import lock, unlock, is_locked, read_lock
from core.utils import enable_stop_all, disable_stop_all


def lock_system(by="system", reason="manual lock"):
    lock(updated_by=by, reason=reason)
    state = set_lock(by=by, note=reason)
    return {
        "ok": True,
        "action": "lock_system",
        "state": state,
        "lock": read_lock(),
    }


def unlock_system(by="system", reason="manual unlock"):
    unlock()
    disable_stop_all()
    state = set_run(by=by, note=reason)
    return {
        "ok": True,
        "action": "unlock_system",
        "state": state,
        "lock": read_lock(),
    }


def stop_system(by="system", reason="manual stop"):
    enable_stop_all()
    state = set_stop(by=by, note=reason)
    return {
        "ok": True,
        "action": "stop_system",
        "state": state,
        "lock": read_lock(),
    }


def get_system_flags():
    return {
        "locked": is_locked(),
        "lock_info": read_lock(),
    }

