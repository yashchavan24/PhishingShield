import json
import os
import threading

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "threats.json")

_LOCK = threading.RLock()
_CACHE = None


def load_db():
    """Return the full threat database as a dict (never raises).

    The file is cached in memory; the clipboard thread opened the JSON file
    dozens of times per second, which caused random 'file in use' crashes
    on Windows when a save raced a read.
    """
    global _CACHE
    with _LOCK:
        if _CACHE is not None:
            return _CACHE
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                _CACHE = json.load(f)
        except FileNotFoundError:
            _CACHE = {}
        except (json.JSONDecodeError, OSError):
            # Corrupt file: back it up instead of crashing the whole app
            try:
                if os.path.exists(DB_PATH):
                    os.replace(DB_PATH, DB_PATH + ".corrupt.bak")
            except OSError:
                pass
            _CACHE = {}
        if not isinstance(_CACHE, dict):
            _CACHE = {}
        return _CACHE


def save_db(data):
    """Persist the database atomically (tmp file + os.replace)."""
    global _CACHE
    with _LOCK:
        try:
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            tmp = DB_PATH + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, DB_PATH)
            _CACHE = data
        except OSError:
            # Last-resort non-atomic save so a report is never silently lost
            try:
                with open(DB_PATH, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                _CACHE = data
            except OSError:
                pass


def get_entry(email):
    """Return one entry as a dict, creating it lazily if missing."""
    db = load_db()
    entry = db.get(email)
    if not isinstance(entry, dict):
        entry = {"reports": 0, "blocked_by": [], "category": "Unknown", "first_seen": ""}
        db[email] = entry
    return entry


def record_report(email, device_id):
    """Add one community report to an email (in-memory only until save_db)."""
    email = email.strip().lower()
    with _LOCK:
        entry = get_entry(email)
        entry["reports"] = entry.get("reports", 0) + 1
        if device_id and device_id not in entry.get("blocked_by", []):
            entry.setdefault("blocked_by", []).append(device_id)
        if not entry.get("first_seen"):
            from datetime import date
            entry["first_seen"] = str(date.today())
    return entry


def get_stats():
    """(total_reports, confirmed_phishing) across the whole database."""
    with _LOCK:
        db = load_db()
        total = 0
        confirmed = 0
        for v in db.values():
            if not isinstance(v, dict):
                continue
            reports = v.get("reports", 0)
            total += reports
            if reports >= 10:
                confirmed += 1
        return total, confirmed
