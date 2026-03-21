import json
import os
import socket
import subprocess
import time
from pathlib import Path

import psutil

from core.config import SERVER_LOCK, STOP_ALL_LOCK


def run(cmd: list[str], timeout: int = 15) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (result.stdout or "").strip()
    except Exception as e:
        return f"error: {e}"


def file_is_on(path: str) -> bool:
    return Path(path).exists()


def get_hostname() -> str:
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"


def get_uptime_text() -> str:
    try:
        uptime = int(time.time() - psutil.boot_time())
        days = uptime // 86400
        hours = (uptime % 86400) // 3600
        minutes = (uptime % 3600) // 60
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours or days:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        return " ".join(parts)
    except Exception:
        return "unknown"


def get_load_text() -> str:
    try:
        load1, load5, load15 = os.getloadavg()
        return f"{load1:.2f} / {load5:.2f} / {load15:.2f}"
    except Exception:
        return "unknown"


def get_cpu_percent() -> int:
    try:
        return int(psutil.cpu_percent(interval=1))
    except Exception:
        return 0


def get_ram_info() -> tuple[int, int, int]:
    try:
        vm = psutil.virtual_memory()
        used_mb = int(vm.used / 1024 / 1024)
        total_mb = int(vm.total / 1024 / 1024)
        return int(vm.percent), used_mb, total_mb
    except Exception:
        return 0, 0, 0


def get_disk_info() -> tuple[int, str]:
    try:
        du = psutil.disk_usage("/")
        used_gb = du.used / 1024 / 1024 / 1024
        total_gb = du.total / 1024 / 1024 / 1024
        return int(du.percent), f"{used_gb:.1f}G/{total_gb:.1f}G"
    except Exception:
        return 0, "unknown"


def bar(percent: int, width: int = 10) -> str:
    percent = max(0, min(100, int(percent)))
    filled = percent * width // 100
    empty = width - filled
    return "█" * filled + "░" * empty


def service_state(name: str) -> str:
    raw = run(["systemctl", "is-active", name])
    if raw.strip() == "active":
        return "✅ RUNNING"
    return "❌ DOWN"


def pm2_status_text() -> str:
    raw = run(["pm2", "jlist"], timeout=20)
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


def lock_state_text() -> str:
    server_lock = "🔒 ON" if file_is_on(SERVER_LOCK) else "🟢 OFF"
    stop_all = "🛑 ON" if file_is_on(STOP_ALL_LOCK) else "🟢 OFF"
    return (
        f"🔐 SERVER LOCK: {server_lock}\n"
        f"🛑 STOP ALL: {stop_all}"
    )


def read_net_dev() -> dict[str, tuple[int, int]]:
    stats: dict[str, tuple[int, int]] = {}
    with open("/proc/net/dev", "r", encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if not parts or ":" not in parts[0]:
                continue
            iface = parts[0].rstrip(":")
            rx = int(parts[1])
            tx = int(parts[9])
            stats[iface] = (rx, tx)
    return stats


def fmt_rate(value: int) -> str:
    if value >= 1024 * 1024:
        return f"{value / 1024 / 1024:.1f} MB/s"
    if value >= 1024:
        return f"{value / 1024:.1f} KB/s"
    return f"{value} B/s"


def get_traffic_text() -> str:
    try:
        s1 = read_net_dev()
        time.sleep(1)
        s2 = read_net_dev()

        rx_total = 0
        tx_total = 0

        for iface, (rx2, tx2) in s2.items():
            if iface == "lo" or iface not in s1:
                continue
            rx1, tx1 = s1[iface]
            rx_total += max(0, rx2 - rx1)
            tx_total += max(0, tx2 - tx1)

        return f"📥 IN: {fmt_rate(rx_total)}\n📤 OUT: {fmt_rate(tx_total)}"
    except Exception as e:
        return f"traffic error: {e}"


def get_connections_text(limit: int = 8) -> str:
    raw = run(["ss", "-tunap"], timeout=20)
    lines = raw.splitlines()
    seen: dict[str, int] = {}

    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 6:
            continue
        peer = parts[5]
        if peer.startswith("["):
            addr = peer.rsplit("]:", 1)[0].strip("[]")
        else:
            addr = peer.rsplit(":", 1)[0]

        if addr in ("*", "0.0.0.0", "::", "[::]", "127.0.0.1", "::1", ""):
            continue

        seen[addr] = seen.get(addr, 0) + 1

    if not seen:
        return "  no external connections"

    top = sorted(seen.items(), key=lambda x: -x[1])[:limit]
    return "\n".join(f"  {ip} ({count})" for ip, count in top)


def get_status_text() -> str:
    cpu = get_cpu_percent()
    ram_pct, ram_used, ram_total = get_ram_info()
    disk_pct, disk_used = get_disk_info()

    return (
        "⚡ APEX SERVER STATUS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🖥 HOST: {get_hostname()}\n"
        f"⏱ UPTIME: {get_uptime_text()}\n"
        f"📈 LOAD: {get_load_text()}\n\n"
        f"🧠 CPU  {bar(cpu)} {cpu}%\n"
        f"🧠 RAM  {bar(ram_pct)} {ram_pct}% ({ram_used}MB/{ram_total}MB)\n"
        f"💾 DISK {bar(disk_pct)} {disk_pct}% ({disk_used})\n\n"
        f"{lock_state_text()}\n\n"
        f"🛠 COCKPIT: {service_state('cockpit')}\n"
        f"🛡 FAIL2BAN: {service_state('fail2ban')}\n\n"
        f"📦 PM2 SERVICES:\n{pm2_status_text()}"
    )


def get_services_text() -> str:
    return (
        "🤖 SERVICES\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🛠 Cockpit: {service_state('cockpit')}\n"
        f"🛡 Fail2ban: {service_state('fail2ban')}\n"
        f"📦 PM2:\n{pm2_status_text()}"
    )


def get_test_text() -> str:
    return (
        "🧪 TEST OK\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"HOST: {get_hostname()}\n"
        "Bot is alive and responding."
    )


def get_modes_text() -> str:
    server_lock_on = file_is_on(SERVER_LOCK)
    stop_all_on = file_is_on(STOP_ALL_LOCK)

    safe_mode = "🔒 ENABLED" if server_lock_on else "🟢 DISABLED"
    stop_all = "🛑 ENABLED" if stop_all_on else "🟢 DISABLED"

    return (
        "🛡 MODES / SAFETY\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"SAFE MODE: {safe_mode}\n"
        f"STOP ALL: {stop_all}"
    )


def enable_server_lock() -> None:
    Path(SERVER_LOCK).touch()


def disable_server_lock() -> None:
    Path(SERVER_LOCK).unlink(missing_ok=True)


def toggle_server_lock() -> str:
    if file_is_on(SERVER_LOCK):
        disable_server_lock()
        return "🟢 SERVER LOCK DISABLED"
    enable_server_lock()
    return "🔒 SERVER LOCK ENABLED"


def enable_stop_all() -> None:
    Path(STOP_ALL_LOCK).touch()


def disable_stop_all() -> None:
    Path(STOP_ALL_LOCK).unlink(missing_ok=True)
