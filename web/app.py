"""
Phishing Shield — web backend (Flask/WSGI).

Single entrypoint that Vercel runs for every request: serves the static
frontend AND the JSON API. Locally:

    cd web && python devserver.py     ->  http://127.0.0.1:8000
"""
import os
import json

from flask import Flask, request, jsonify, send_from_directory

from checker import check_email, is_email
from reporter import report_email, get_device_id
from database import get_stats, load_db

HERE = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=None)


# ── static frontend ─────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(HERE, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    if filename in ("style.css", "app.js"):
        return send_from_directory(HERE, filename)
    return jsonify(error="not found"), 404


# ── API ─────────────────────────────────────────────────────────
@app.route("/api/health")
def api_health():
    return jsonify(status="ok")


@app.route("/api/check", methods=["POST"])
def api_check():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip()
    if not is_email(email):
        return jsonify(error="invalid email address"), 400
    result = check_email(email)
    resp = jsonify(result)
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/api/report", methods=["POST"])
def api_report():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip()
    if not is_email(email):
        return jsonify(error="invalid email address"), 400
    return jsonify(message=report_email(email), device=get_device_id())


@app.route("/api/stats")
def api_stats():
    total, confirmed = get_stats()
    db = load_db()
    suspicious = sum(1 for v in db.values()
                     if isinstance(v, dict) and 1 <= v.get("reports", 0) < 10)
    categories = {}
    for v in db.values():
        if isinstance(v, dict):
            categories[v.get("category", "Unknown")] = \
                categories.get(v.get("category", "Unknown"), 0) + 1
    return jsonify(entries=len(db), total_reports=total, confirmed=confirmed,
                   suspicious=suspicious, categories=categories)


@app.route("/api/threats")
def api_threats():
    q = (request.args.get("q") or "").lower()
    filt = (request.args.get("filter") or "").upper()
    out = []
    for email, v in load_db().items():
        if not isinstance(v, dict):
            continue
        r = v.get("reports", 0)
        status = "PHISHING" if r >= 10 else ("SUSPICIOUS" if r >= 1 else "SAFE")
        if filt and filt != "ALL" and status != filt:
            continue
        if q and q not in email.lower() and q not in v.get("category", "").lower():
            continue
        out.append({"email": email, "reports": r, "status": status,
                    "category": v.get("category", "Unknown"),
                    "first_seen": v.get("first_seen", "")})
    out.sort(key=lambda t: -t["reports"])
    return jsonify(count=len(out), threats=out)


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT") or 8000)
    app.run(host="127.0.0.1", port=PORT, debug=False)
