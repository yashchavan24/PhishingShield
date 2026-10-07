"""
Phishing Shield — offline demo & integration server.

Serves the REST API on http://127.0.0.1:5000 so the desktop app (or the
web app) has a bridge to shared data **without needing the internet**.

    python server.py            ->  http://127.0.0.1:5000/ui   (demo GUI)
    python server.py --no-ui    ->  API-only, headless

Endpoints (identical to the Vercel deployment, so this file doubles as
a local backend for the web app):
    GET  /api/health
    GET  /api/stats
    POST /api/check   {"email": "..."}
    POST /api/report  {"email": "..."}
    GET  /api/threats?q=&filter=
POST /api/check and /api/report share an os.environ PHISH_THRESHOLD.
"""
import os
import json
import threading
import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import checker
import database
from reporter import report_email, get_device_id

DB_PATH = database.DB_PATH

_lock = threading.Lock()


def _body(handler):
    length = int(handler.headers.get("Content-Length") or 0)
    if length > 8192:
        return {}
    raw = handler.rfile.read(length) if length else b"{}"
    try:
        data = json.loads(raw.decode("utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


class Handler(BaseHTTPRequestHandler):
    server_version = "PhishingShield/2.1"

    # ── CORS (so the web frontend on another origin can call this API) ──
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass                          # keep the demo output clean

    # ── small HTML demo page (zero dependencies) ──
    def _ui(self):
        html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Phishing Shield — Demo</title>
<style>
 body{background:#070b14;color:#f1f5f9;font-family:Segoe UI,sans-serif;
      display:flex;flex-direction:column;align-items:center;padding-top:8vh}
 h1{color:#06b6d4;margin:0}
 p{color:#94a3b8}
 input{background:#111827;border:1px solid #1e3a5f;color:#f1f5f9;
       padding:12px 14px;border-radius:10px;width:min(420px,86vw);font-size:15px}
 button{background:#06b6d4;border:0;color:#062033;font-weight:700;
        padding:12px 22px;border-radius:10px;cursor:pointer;margin-top:12px}
 .res{margin-top:20px;padding:18px;border-radius:12px;width:min(520px,88vw);
      border:1px solid #1e3a5f;background:#0f172a;white-space:pre-wrap}
 .red{border-color:#ef4444!important;color:#ef4444!important}
 .yel{border-color:#f59e0b!important;color:#f59e0b!important}
 .grn{border-color:#10b981!important;color:#10b981!important}
</style></head><body>
<h1>&#128737; Phishing Shield</h1>
<p>Offline demo &mdash; community threat database</p>
<input id="e" placeholder="paste any email address..." autocapitalize="off"/>
<br/><button onclick="go()">Scan Email</button>
<div class="res" id="r">Scan a suspicious address to see the verdict.</div>
<script>
function go(){
  fetch('/api/check',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:document.getElementById('e').value})})
    .then(r=>r.json()).then(d=>{
      const el=document.getElementById('r');
      el.textContent=d.status+'  -  '+d.email+'\n'+d.reasons.join('\n');
      el.className='res '+((d.status||'').includes('PHISHING')?'red':(d.status||'').includes('SUSPICIOUS')?'yel':'grn');
    });
}
</script></body></html>"""
        data = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ── routes ──
    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if not self.path.startswith("/api/"):
            if self.path in ("/", "/ui", "/index.html"):
                self._ui()
            else:
                self._send(404, {"error": "not found"})
            return
        route = self.path.split("?")[0]
        if route == "/api/health":
            self._send(200, {"status": "ok"})
        elif route == "/api/stats":
            total, confirmed = database.get_stats()
            db = database.load_db()
            suspicious = sum(1 for v in db.values()
                             if isinstance(v, dict) and 1 <= v.get("reports", 0) < 10)
            self._send(200, {"total_reports": total, "confirmed": confirmed,
                             "suspicious": suspicious, "entries": len(db)})
        elif route == "/api/threats":
            self._send(200, database.load_db())
        else:
            self._send(404, {"error": "unknown endpoint"})

    def do_POST(self):
        route = self.path.split("?")[0]
        if route == "/api/check":
            data = _body(self)
            email = str(data.get("email", "")).strip()
            if not checker.is_email(email):
                self._send(400, {"error": "invalid email"})
                return
            self._send(200, checker.check_email(email))
        elif route == "/api/report":
            data = _body(self)
            email = str(data.get("email", "")).strip()
            if not checker.is_email(email):
                self._send(400, {"error": "invalid email"})
                return
            self._send(200, {"message": report_email(email),
                             "device": get_device_id()})
        else:
            self._send(404, {"error": "unknown endpoint"})


def main():
    ap = argparse.ArgumentParser(description="Phishing Shield offline API")
    ap.add_argument("--port", type=int, default=5000)
    ap.add_argument("--no-ui", action="store_true", help="API only, no HTML at /")
    args = ap.parse_args()
    database.load_db()            # fail fast if the DB dir cannot be created
    httpd = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    url = f"http://{'127.0.0.1' if args.no_ui else '127.0.0.1'}:{args.port}"
    print(f"[Phishing Shield] API ready -> {url}/api/health "
          f"({'UI at / if served' if not args.no_ui else 'API-only mode'})")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
