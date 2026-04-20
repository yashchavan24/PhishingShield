import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "threats.json")

def load_db():
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2)

def get_stats():
    db = load_db()
    total_reports = sum(v["reports"] for v in db.values())
    confirmed = sum(1 for v in db.values() if v["reports"] >= 10)
    return total_reports, confirmed