import os


def get_cpu_load():
    try:
        load1, load5, load15 = os.getloadavg()
        return {
            "load_1m": round(load1, 2),
            "load_5m": round(load5, 2),
            "load_15m": round(load15, 2),
        }
    except Exception as e:
        return {"error": str(e)}


def get_uptime():
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
        return round(uptime_seconds, 0)
    except Exception as e:
        return {"error": str(e)}


def get_ram():
    try:
        meminfo = {}
        with open("/proc/meminfo", "r") as f:
            for line in f:
                key, value = line.split(":")
                meminfo[key] = int(value.strip().split()[0])

        total = meminfo.get("MemTotal", 0)
        free = meminfo.get("MemAvailable", 0)
        used = total - free

        percent = (used / total * 100) if total > 0 else 0

        return {
            "total_mb": round(total / 1024, 0),
            "used_mb": round(used / 1024, 0),
            "percent": round(percent, 2),
        }
    except Exception as e:
        return {"error": str(e)}


def get_disk():
    try:
        st = os.statvfs("/")
        total = st.f_blocks * st.f_frsize
        free = st.f_bavail * st.f_frsize
        used = total - free

        percent = (used / total * 100) if total > 0 else 0

        return {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "percent": round(percent, 2),
        }
    except Exception as e:
        return {"error": str(e)}


def get_monitor_snapshot():
    return {
        "cpu": get_cpu_load(),
        "ram": get_ram(),
        "disk": get_disk(),
        "uptime_sec": get_uptime(),
    }
