import uuid
import os
import json
from database import load_db, save_db
from datetime import date

DEVICE_LOG = "device_log.json"

def get_device_id():
    return str(uuid.getnode())

def load_device_log():
    if not os.path.exists(DEVICE_LOG):
        return {}
    with open(DEVICE_LOG, "r") as f:
        return json.load(f)

def save_device_log(log):
    with open(DEVICE_LOG, "w") as f:
        json.dump(log, f, indent=2)

def report_email(email: str) -> str:
    email = email.strip().lower()
    device_id = get_device_id()
    today = str(date.today())
    log_key = f"{device_id}_{email}_{today}"

    device_log = load_device_log()
    if log_key in device_log:
        return "⚠️ You already reported this email today from this device."

    db = load_db()
    if email not in db:
        db[email] = {"reports": 0, "blocked_by": []}

    db[email]["reports"] += 1
    db[email]["blocked_by"].append(device_id)
    save_db(db)

    device_log[log_key] = True
    save_device_log(device_log)

    return f"✅ Reported! Total reports for this email: {db[email]['reports']}"