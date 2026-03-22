import json
import os
import socket
import subprocess
from pathlib import Path

from core.config import STOP_ALL_LOCK
from core.state import load_state
from core.lock import is_locked
from core.monitor import get_monitor_snapshot
from core.services import get_services_status
from core.safety import evaluate_safety


def run_cmd(cmd, timeout=15):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (result.stdout or "").strip()
    except Exception as e:
        return f"error: {e}"


def get_hostname():
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"


def get_uptime_text(uptime_sec):
    try:
        uptime = int(float(uptime_sec))
        days = uptime // 86400
        hours = (uptime % 86400) // 3600
        minutes = (uptime % 3600) // 60

        parts = []
        if days:
            parts.append(f"{days}d")
        if days or hours:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        return " ".join(parts)
    except Exception:
        return "unknown"


def bar(percent, width=10):
    try:
        percent = float(percent)
    except Exception:
        percent = 0.0

    if percent < 0:
        percent = 0.0
    if percent > 100:
        percent = 100.0

    filled = int(percent * width // 100)
    empty = width - filled
    return "█" * filled + "░" * empty


def cpu_percent_from_load(cpu_data):
    try:
        import psutil
        return round(psutil.cpu_percent(interval=1), 0)
    except Exception:
        return 0.0


def get_ram_details():
    try:
        meminfo = {}
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            for line in f:
                key, value = line.split(":")
                meminfo[key] = int(value.strip().split()[0])

        total_mb = int(meminfo.get("MemTotal", 0) / 1024)
        avail_mb = int(meminfo.get("MemAvailable", 0) / 1024)
        used_mb = total_mb - avail_mb

        return used_mb, total_mb
    except Exception:
        return 0, 0


def get_disk_details():
    try:
        st = os.statvfs("/")
        total = st.f_blocks * st.f_frsize
        free = st.f_bavail * st.f_frsize
        used = total - free

        used_gb = used / (1024 ** 3)
        total_gb = total / (1024 ** 3)

        return f"{used_gb:.1f}G/{total_gb:.1f}G"
    except Exception:
        return "unknown"


def pm2_status_text():
    raw = run_cmd(["pm2", "jlist"], timeout=20)
    try:
        data = json.loads(raw)
        if not data:
            return "  no processes found"

        lines = []
        for proc in data:
            name = proc.get("name", "unknown")
            status = proc.get("pm2_env", {}).get("status", "unknown")
            icon = "✅" if status == "online" else "❌"
            lines.append(f"  {icon} {name}")
        return "\n".join(lines)
    except Exception:
        return "  ⚠️ pm2 unavailable"


def lock_state_text():
    server_lock = "🔒 ON" if is_locked() else "🟢 OFF"
    stop_all = "🛑 ON" if Path(STOP_ALL_LOCK).exists() else "🟢 OFF"
    return (
        f"🔐 SERVER LOCK: {server_lock}\n"
        f"🛑 STOP ALL: {stop_all}"
    )


def service_line(name, status):
    icon = "✅" if status == "OK" else "❌"
    label = name.upper()
    value = "RUNNING" if status == "OK" else "DOWN"
    return f"{icon} {label}: {value}"


def build_status_text():
    state = load_state()
    monitor = get_monitor_snapshot()
    services = get_services_status()
    safety = evaluate_safety()

    cpu = monitor.get("cpu", {})
    ram = monitor.get("ram", {})
    disk = monitor.get("disk", {})
    uptime_sec = monitor.get("uptime_sec", 0)

    cpu_pct = cpu_percent_from_load(cpu)
    ram_pct = float(ram.get("percent", 0) or 0)
    disk_pct = float(disk.get("percent", 0) or 0)

    ram_used, ram_total = get_ram_details()
    disk_used = get_disk_details()

    text = (
        "⚡ APEX SERVER STATUS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🖥 HOST: {get_hostname()}\n"
        f"⏱ UPTIME: {get_uptime_text(uptime_sec)}\n"
        f"📈 LOAD: {cpu.get('load_1m', 0)} / {cpu.get('load_5m', 0)} / {cpu.get('load_15m', 0)}\n\n"
        f"🧠 CPU  {bar(cpu_pct)} {int(cpu_pct)}%\n"
        f"🧠 RAM  {bar(ram_pct)} {round(ram_pct)}% ({ram_used}MB/{ram_total}MB)\n"
        f"💾 DISK {bar(disk_pct)} {round(disk_pct)}% ({disk_used})\n\n"
        f"{lock_state_text()}\n\n"
        f"🛠 COCKPIT: {service_line('cockpit', services.get('cockpit', 'FAIL')).split(': ', 1)[1]}\n"
        f"🛡 FAIL2BAN: {service_line('fail2ban', services.get('fail2ban', 'FAIL')).split(': ', 1)[1]}\n\n"
        f"📦 PM2 SERVICES:\n{pm2_status_text()}\n\n"
        f"🛡 SAFETY: {safety.get('status', 'UNKNOWN')}"
    )

    warnings = safety.get("warnings", [])
    if warnings:
        text += "\n" + "\n".join(f"⚠️ {w}" for w in warnings)

    return text


async def handle_status(update, context) -> None:
    await update.message.reply_text(build_status_text())
