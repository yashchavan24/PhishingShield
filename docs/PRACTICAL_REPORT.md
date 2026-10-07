# 📘 PROJECT REPORT — PHISHING SHIELD

**6th Semester Major Project · Dept. of CSE (Cyber Security) · SVPCET, Nagpur — 2026**

---

## 1. AIM

To design and develop **"Phishing Shield" — a community-powered email phishing
detection system** (desktop application + web application + REST API) that
identifies malicious sender email addresses in real time using a
crowd-sourced threat database and a rule-based heuristic engine, and alerts
the user within one second — just as Truecaller identifies spam phone calls.

---

## 2. TOOLS USED

| # | Tool / Technology | Purpose |
|---|---|---|
| 1 | **Python 3** | Core programming language |
| 2 | **Tkinter** | Desktop GUI (login, dashboard, scanner, database, statistics) |
| 3 | **Pyperclip + Threading + queue.Queue** | Real-time clipboard monitoring in the background |
| 4 | **JSON** | Lightweight database storing threats, reports and users |
| 5 | **SHA-256 (hashlib)** | Secure password & device-ID hashing |
| 6 | **HTML5, CSS3, JavaScript** | Web frontend (responsive dark-themed UI) |
| 7 | **Flask (Python WSGI)** | Web backend / REST API |
| 8 | **Vercel (serverless)** | Hosting & deployment of the web app |
| 9 | **Git & GitHub** | Version control and source hosting |
| 10 | **PyInstaller** | Packaging the desktop app into a `.exe` |
| 11 | **VS Code** | Code editor |
| 12 | **curl / browser dev-tools** | API and UI testing |

---

## 3. PROBLEM STATEMENT

Every day students receive phishing emails that imitate banks, colleges,
shopping sites and government schemes:

- *"Your SBI account will be suspended in 24 hours — verify now"*
- *"SVPCET fee payment pending — pay at http://svp-fee-notice.com"*
- *"You won a Jio lottery of ₹25,00,000 — claim your prize"*

These scams succeed because:

1. Gmail's spam filter misses sophisticated or newly-created phishing domains.
2. Students have **no quick way** to verify whether an unknown sender is safe.
3. Once one student falls for a scam, others in the same college receive the
   **same** phishing email — the knowledge is never shared.

**Therefore:** there is a need for a shared, community-driven shield where
**one person's discovery protects everyone** — implemented exactly like
Truecaller does for spam calls.

---

## 4. METHODS USED

### 4.1 Software Development Model
Incremental model — built module-by-module (checker → reporter → GUI →
web/API), each increment tested before the next.

### 4.2 System Architecture

```
   ┌─────────────┐   copy event    ┌──────────────────┐
   │   User      │ ─────────────▶  │ Clipboard Monitor │ (background thread,
   └─────────────┘                 └────────┬─────────┘  1-second poll, queue)
                                            │ valid email?
                                            ▼
                      ┌─────────────────────────────────────┐
                      │           CHECKER ENGINE             │
                      │ 1. Whitelist (banks, .gov.in, .ac.in)│
                      │ 2. Community DB (report count)       │
                      │ 3. Heuristic scoring (lexical rules) │
                      └────────────┬────────────────────────┘
                                   │ verdict < 1 s
                    SAFE ▼      SUSPICIOUS ▼      PHISHING ▼
                  (green)      (1–9 reports)     (10+ reports or
                                 + warning         score ≥ 3) + alert
                                   │
                             [ REPORT / BLOCK ]
                                   │
                     threat DB updated → protects ALL users
```

### 4.3 Detection Logic (3 layers)

1. **Whitelist layer** — verified genuine domains (`sbi.co.in`, `google.com`,
   `svpcet.ac.in`, `gov.in` …) are always SAFE. Prevents false positives.
2. **Community layer** — every user can report a malicious address; counts are
   stored in `db/threats.json`. Threshold: 1–9 reports = **SUSPICIOUS**,
   10+ = **PHISHING**. Rate-limited to **1 report per device per email per
   day** (device-log with SHA-256 hashed device IDs) to stop spam reporting.
3. **Heuristic layer (new in v3.0)** — lexical analysis of the address itself,
   so even a **never-seen-before** scam gets flagged with **0 reports**:
   - Suspicious free/cheap TLDs: `.tk .ml .xyz .top .click .link …` (+2)
   - Typosquat/look-alike domains: `paypa1`, `g00gle`, `micros0ft` (+3)
   - Recognised brand names in unverified domains (+1)
   - Urgency keywords in the local part: `verify`, `kyc`, `suspended`,
     `urgent`, `prize`, `winner` … (+1 each, max +2)
   - Mostly-numeric local part (+1)
   - Score ≥ 3 ⇒ PHISHING, score 1–2 ⇒ SUSPICIOUS, each verdict includes
     human-readable **reasons** ("suspicious TLD .top", "impersonates 'paypal'").

### 4.4 Data Flow & Storage
- `db/threats.json` — email → { reports, blocked_by[], category, first_seen }
- Atomic writes (temp-file + `os.replace`) and in-memory caching make the
  database corruption-proof and thread-safe.
- `users.json` — login credentials stored **only as SHA-256 hashes**.

### 4.5 User Interfaces
- **Desktop (Tkinter):** Login → Dashboard (live threat feed, top threats,
  quick scan) → Manual Scan → Threat Database (search/filter) → Statistics →
  About. Dark cyber-security theme (cyan/purple on navy).
- **Web (HTML/CSS/JS + Flask):** scanner with verdict reasons, live threat
  table with search & filters, statistics cards, REST API documentation
  section, shareable scan links (`/?email=...`).

### 4.6 API Design (backend - Flask, deployed on Vercel)

| Method | Endpoint | Function |
|---|---|---|
| POST | `/api/check` | Returns verdict {status, reports, heuristics, reasons[], source} |
| POST | `/api/report` | Adds a community report with device rate-limit |
| GET | `/api/stats` | Aggregated statistics & category counts |
| GET | `/api/threats` | Searchable / filterable threat list |
| GET | `/api/health` | Health probe |

### 4.7 Testing Done
- Unit tests of the checker engine (whitelist, DB hit, heuristic-only hits,
  invalid input → 400).
- Concurrency testing (clipboard thread + GUI main thread via queue).
- Crash-fix verification: Tkinter `trace_add`, stale-widget guards,
  corruption-resilient DB, atomic saves.
- API tests on the live deployment (200/400 responses, filters, reports).

---

## 5. FUTURE SCOPE

1. **Gmail API integration** — scan the inbox automatically, not just copies.
2. **Browser extension** — one-click verdict inside Gmail/Outlook web.
3. **Machine learning** — train a Naive Bayes / Random-Forest classifier on
   labelled phishing datasets (Kaggle, UCI) to replace hand-written rules.
4. **URL & attachment scanning** — check links inside emails using
   Google Safe Browsing / VirusTotal APIs.
5. **Central cloud database** — sync community reports across all devices in
   real time (college-wide → city-wide → national student network).
6. **Authentication hardening** — bcrypt + salt, OTP login, admin panel.
7. **Regional language warnings** — Hindi/Marathi alerts for wider reach.
8. **Mobile app** — Android version with notification support.

---

## 6. CONCLUSION

Phishing Shield demonstrates that **a community of ordinary users, armed with
a smart rule engine, can defeat a threat that even commercial spam filters
miss.** The project delivered a complete working system across three platform
levels — a desktop Tkinter application, a responsive web application, and a
public REST API deployed on Vercel — all sharing the same detection engine.

The three-layer verdict pipeline (whitelist → community reports → heuristics)
rafts an important property: it detects **known** scams instantly through the
database, and **unknown/zero-day** scams through lexical heuristics, while the
anti-abuse design (whitelist, thresholds, device rate-limits, hashed IDs)
keeps the system trustworthy. The system is free, needs no special
permissions, stores data locally, and works offline — making it practical for
students and teachable as a cybersecurity project.

Through this project we learned: secure coding practices (hashing, atomic
writes, input validation), concurrent programming (threads + queues + Tkinter
thread-safety), REST API design, serverless deployment, and the real-world
behaviour of phishing attacks.

**Result: Fully working desktop + web deployment —
https://phishing-shield-navy.vercel.app**

---

## 7. REFERENCES

1. APWG (Anti-Phishing Working Group) — Phishing Activity Trends Report.
2. RBI — "Modus Operandi of Cyber Frauds" public advisories.
3. RFC 5322 — Internet Message Format (email address syntax).
4. Flask documentation — https://flask.palletsprojects.com
5. Vercel Functions docs — https://vercel.com/docs/functions
6. OWASP — Phishing & Social Engineering prevention cheat-sheet.
