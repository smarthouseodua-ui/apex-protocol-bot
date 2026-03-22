from core.actions import lock_system, unlock_system, stop_system
from core.lock import is_locked


def cmd_lock(user="system"):
    return lock_system(by=user, reason="manual lock via control")


def cmd_unlock(user="system"):
    return unlock_system(by=user, reason="manual unlock via control")


def cmd_stop(user="system"):
    return stop_system(by=user, reason="manual stop via control")


def get_control_menu():
    locked = is_locked()

    return {
        "lock": "LOCK 🔒",
        "unlock": "UNLOCK 🔓",
        "stop": "STOP 🛑",
        "state": "LOCKED" if locked else "UNLOCKED",
    }
