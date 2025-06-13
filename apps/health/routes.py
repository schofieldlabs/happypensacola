import os
from flask import Blueprint, request, abort, current_app
from datetime import datetime

health_bp = Blueprint('health', __name__)

# UptimeRobot IP addresses as of June 2025
# (always double-check with https://uptimerobot.com/inc/files/ips.txt periodically)
# https://uptimerobot.com/inc/files/ips/IPv4andIPv6.txt
ALLOWED_IPS = [
    "69.162.124.226",
    "69.162.124.227",
    "69.162.124.228",
    "69.162.124.229",
    "69.162.124.230",
    "69.162.124.231",
    "69.162.124.232",
    "69.162.124.233",
    "69.162.124.234",
    "69.162.124.235",
    "69.162.124.236",
    "69.162.124.237",
    "69.162.124.238",
    "69.162.124.239",
    "69.162.124.240",
    "68.225.71.120", # This is me on 6/12/25
    "69.162.124.224",
    "69.162.124.225",
    "216.144.248.16",
    "216.144.248.17",
    "216.144.248.18",
    "216.144.248.19",
    "216.144.248.20",
    "216.144.248.21",
    "216.144.248.22",
    "216.144.248.23",
    "216.144.248.24",
    "216.144.248.25",
    "216.144.248.26",
    "216.144.248.27",
    "216.144.248.28",
    "216.245.221.80",
    "3.212.128.62",
    "34.198.201.66",
    "52.22.236.30",
    "54.167.223.174",
    "3.12.251.153",
    "3.20.63.178",
    "18.116.205.62",
    "52.15.147.27",
    "35.84.118.171",
    "35.166.228.98",
    "44.227.38.253",
    "104.131.107.63",
    "165.227.83.148",
    "138.197.150.151",
    "159.203.30.41",
    "5.161.61.238",
    "5.161.75.7",
    "5.78.87.38",
    "5.78.118.142"
]

# User-Agent allowlist (covers external monitors + GitHub Action)
ALLOWED_USER_AGENTS = [
    "UptimeRobot",
    "BetterUptime",
    "curl",
    "GitHub"
]

@health_bp.route('/health', methods=['GET'])
def health():
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')

    # IP allowlist (only enforce if ALLOWED_IPS is non-empty)
    if ALLOWED_IPS and client_ip not in ALLOWED_IPS:
        log_access_denied(client_ip, user_agent, reason="IP not allowed")
        abort(403)

    # User-Agent allowlist (broad but safe)
    if not any(allowed_ua in user_agent for allowed_ua in ALLOWED_USER_AGENTS):
        log_access_denied(client_ip, user_agent, reason="User-Agent not allowed")
        abort(403)

    return 'OK', 200

def log_access_denied(ip, ua, reason=""):
    now = datetime.utcnow().isoformat()
    current_app.logger.warning(f"[{now}] Healthcheck access denied: IP={ip}, User-Agent='{ua}', Reason={reason}")
