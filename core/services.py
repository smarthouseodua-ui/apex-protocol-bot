import subprocess


def _run(cmd):
    try:
        result = subprocess.getoutput(cmd)
        return result.strip()
    except Exception as e:
        return f"error: {e}"


def check_pm2():
    out = _run("pm2 list")
    if "online" in out.lower():
        return "OK"
    return "FAIL"


def check_cockpit():
    out = _run("systemctl is-active cockpit")
    return "OK" if "active" in out else "FAIL"


def check_fail2ban():
    out = _run("systemctl is-active fail2ban")
    return "OK" if "active" in out else "FAIL"


def get_services_status():
    return {
        "pm2": check_pm2(),
        "cockpit": check_cockpit(),
        "fail2ban": check_fail2ban(),
    }
