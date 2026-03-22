from core.monitor import get_monitor_snapshot
from core.services import get_services_status


def evaluate_safety():
    monitor = get_monitor_snapshot()
    services = get_services_status()

    status = "OK"
    warnings = []

    # RAM
    ram = monitor.get("ram", {})
    if isinstance(ram, dict) and ram.get("percent", 0) > 90:
        status = "WARN"
        warnings.append("HIGH RAM USAGE")

    # DISK
    disk = monitor.get("disk", {})
    if isinstance(disk, dict) and disk.get("percent", 0) > 95:
        status = "CRITICAL"
        warnings.append("DISK ALMOST FULL")

    # SERVICES
    for name, value in services.items():
        if value != "OK":
            status = "WARN"
            warnings.append(f"{name.upper()} DOWN")

    return {
        "status": status,
        "warnings": warnings,
        "monitor": monitor,
        "services": services,
    }
