"""
Community reporting with anti-abuse:
  - one report per device per email per day (rate limit)
  - SHA-256 of the MAC instead of the raw hardware address (privacy)
  - configurable block threshold (PHISH_THRESHOLD, default 10)
"""
import os
import sys
import json
import uuid
import hashlib
from datetime import date, timedelta

from database import load_db, save_db, record_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, "frozen", False):          # running as a PyInstaller .exe
    BASE_DIR = os.path.dirname(sys.executable)

DEVICE_LOG = os.path.join("/tmp" if os.environ.get("VERCEL") else BASE_DIR, "device_log.json")

BLOCK_CAP = 1000           # max stored blocked_by IDs per email
DEVICE_LOG_CAP = 5000      # keep the rate-limit file from growing forever


def get_device_id():
    """Stable anonymous device fingerprint (SHA-256 of hardware MAC)."""
    node = uuid.getnode()
    return hashlib.sha256(str(node).encode()).hexdigest()[:16]


def load_device_log():
    try:
        with open(DEVICE_LOG, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_device_log(log):
    """Trim the oldest entries so the rate-limit file cannot grow forever."""
    today = date.today().isoformat()
    if len(log) > DEVICE_LOG_CAP:
        for key in list(log.keys())[: len(log) - DEVICE_LOG_CAP]:
            log.pop(key, None)
    tmp = DEVICE_LOG + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2)
        os.replace(tmp, DEVICE_LOG)
    except OSError:
        # last-resort non-atomic write
        try:
            with open(DEVICE_LOG, "w", encoding="utf-8") as f:
                json.dump(log, f, indent=2)
        except OSError:
            pass


def report_email(email: str) -> str:
    """Record one community report. Returns a human-readable message."""
    email = (email or "").strip().lower()
    device_id = get_device_id()
    today = date.today().isoformat()
    log_key = f"{device_id}|{email}|{today}"

    device_log = load_device_log()
    if device_log.get(log_key):
        return "⚠️ You already reported this email today from this device."

    db = load_db()
    if email not in db:
        db[email] = {"reports": 0, "blocked_by": [],
                     "category": "Community Reported"}
    entry = db[email]
    entry["reports"] = entry.get("reports", 0) + 1

    blocked_by = entry.setdefault("blocked_by", [])
    if device_id not in blocked_by:
        blocked_by.insert(0, device_id)
    if len(blocked_by) > BLOCK_CAP:
        del blocked_by[BLOCK_CAP:]

    entry.setdefault("category", "Community Reported")
    if not entry.get("first_seen"):
        entry["first_seen"] = today

    # rate-limit the IP before touching the DB, so a crash never double-counts
    device_log[log_key] = True
    save_device_log(device_log)
    save_db(db)

    threshold = int(os.environ.get("PHISH_THRESHOLD", "10"))
    if entry["reports"] >= threshold:
        return (f"🚫 BLOCKED! {email} now has {entry['reports']} reports "
                f"and is flagged PHISHING for every user.")
    return (f"✅ Reported! {email} now has {entry['reports']} "
            f"{'report' if entry['reports'] == 1 else 'reports'} "
            f"({threshold - entry['reports']} more to auto-block).")


# ── backward-compatible helpers used by tests / docs ──
def check():
    return None
