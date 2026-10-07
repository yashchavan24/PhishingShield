# 🎤 VIVA QUESTIONS & ANSWERS — PHISHING SHIELD

*50 questions from easy to advanced — with confident 2–4 line answers.*

---

## A. BASIC / INTRO QUESTIONS

**1. What is your project in one sentence?**
Phishing Shield is a community-powered email threat detector — like Truecaller,
but for emails — that gives a SAFE / SUSPICIOUS / PHISHING verdict for any
email address within one second.

**2. What problem does it solve?**
Students can't tell whether an unknown sender is real or a scam. My app lets
them check instantly, and when one person reports a scam, everyone gets
protected automatically.

**3. Why is it called "community-powered"?**
Because the threat database is built by its users — every "BLOCK & REPORT"
increases a threat's report count, and at 10 reports it is flagged PHISHING
for every user of the app.

**4. What is phishing?**
Phishing is a cyber-attack where attackers impersonate a trusted organisation
(bank, college, payment app) by email to steal passwords, OTPs, or card
details — usually through fake links with urgency ("your account will be
suspended").

**5. How is phishing different from spam?**
Spam is bulk unwanted advertising; phishing is a targeted fraud attempt to
trick you into revealing data or money. Spam is annoying, phishing is criminal.

**6. Who is your target user?**
College students (starting with SVPCET), but any person or organisation that
wants a free, lightweight email-safety checker.

**7. What platforms does the project run on?**
Three: a desktop app (Python/Tkinter, also packaged as `.exe`), a web app
(HTML/JS + Flask backend), and the REST API behind it, deployed on Vercel.

**8. Is it free to use?**
Yes — fully free, offline capable, and with zero data collection.

---

## B. ARCHITECTURE & WORKING

**9. Explain the overall flow of the system.**
User copies a suspicious email → the clipboard monitor thread detects it each
second → hands it to the checker engine → checker applies 3 layers (whitelist
→ community report count → heuristic score) → verdict with reasons is shown →
the user can report/block it → database updates for everyone.

**10. What are the three verdict levels and their thresholds?**
SAFE (0 reports, clean score), SUSPICIOUS (1–9 reports or heuristic score
1–2), PHISHING (10+ reports or heuristic score ≥ 3).

**11. Why three layers instead of only a database?**
A database only knows *previously reported* scams. The whitelist prevents
false positives on real banks, and the heuristic layer catches brand-new
domains with zero reports — so unknown scams are caught on day one.

**12. What exactly does the heuristic engine check?**
Five lexical rules: suspicious TLDs (.tk/.xyz/.top/.click…), look-alike
brand domains (paypa1/g00gle), brand names in unverified domains, urgency
keywords (verify/kyc/suspended/prize), and mostly-numeric local parts.

**13. Give an example where heuristics catch something the DB can't.**
`verify@netbanking-sbi-alert.top` — brand new, zero reports. SBI appears in a
non-whitelisted domain, the TLD `.top` is heavily abused, and "verify" is an
urgency keyword → heuristic score 4 → PHISHING.

**14. How does the clipboard monitor work?**
A daemon thread polls `pyperclip.paste()` every second; if the new text is a
valid email it evaluates it and puts the verdict in a `queue.Queue`.

**15. Why do you need a Queue? Can't the thread update the GUI directly?**
No — Tkinter is not thread-safe; touching widgets from another thread
crashes randomly. The thread only *enqueues*, and the main thread drains the
queue with `root.after(250, pump)` — this is the standard producer-consumer
pattern.

**16. How does the app behave offline?**
All data is local JSON scanning is pure Python — the desktop works 100%
offline. The web app needs internet only because it's hosted.

**17. What happens when two users report the same email?**
Each device adds 1 to that entry's report count (up to once per device per
day), so multiple users make the count rise faster to the block threshold.

**18. What is the anti-abuse protection?**
Three steps: whitelist (banks can't be mass-reported), thresholding (10
reports needed to auto-block), and a device rate-limit of 1 report per email
per day, stored as a hash of the device ID + date.

**19. Why is the device ID hashed (SHA-256)?**
We need a stable "is this the same device?" key without storing the user's
real hardware MAC — a one-way hash gives identity without privacy leakage.

**20. What data do you store?**
Only what's needed for the job: email address, report count, category, first
seen date, anonymous device-ID hashes. No names, no content of emails, no
personal data.

---

## C. CODE & DESIGN QUESTIONS

**21. How many entries does your database have?**
65 seeded entries covering Banking, Wallet, College, Government, Shopping,
Telecom, Lottery, Travel, Jobs etc., with 1,500+ total community reports —
plus any reports users add live.

**22. Open main.py — how is the login implemented?**
Load credentials from `users.json` (they are SHA-256 hex digests), hash the
entered password with the same algorithm and compare the digests. Registration
creates a new hash. Plaintext passwords are never stored.

**23. Why SHA-256 and not encryption?**
Hashing is one-way — even if the file leaks, attackers can't recover
passwords. Encryption is two-way and reversible with the key, which is a
bigger risk. (Ideally we'd use bcrypt+salt; that is in future scope.)

**24. What is wrong with storing passwords as plaintext?**
Anyone with file access or malware gets the working password immediately.
Hashing means a leak only exposes hashes — infeasible to reverse.

**25. What is a race condition and where could one occur here?**
Two threads writing/reading the JSON simultaneously. I solved it with a
`threading.RLock` around all database access and clipboard-thread isolation
via `queue.Queue`.

**26. How do you write JSON safely?**
Atomic writes: write to a `.tmp` file, then `os.replace()` it into place.
Readers never see a half-written file, and crashes can't corrupt the DB.

**27. What happens if threats.json is corrupted?**
`load_db()` catches the decode error, renames the bad file to
`threats.json.corrupt.bak`, and returns an empty dict — the app keeps working
instead of crashing.

**28. Why JSON and not SQLite?**
For zero configuration, human readability, and easy git-tracked sharing — the
dataset is small. SQLite/Postgres is planned when we move to a central server.

**29. Regex used for email validation?**
`^[\w.!#$%&'*+/=?^_`{|}~-]+@[\w-]+(\.[\w-]+)*\.[A-Za-z]{2,}$` — one local
part, at least one domain, and a TLD of 2+ letters.

**30. Why validate again on the server side when the web form already checks?**
Client-side checks prevent honest mistakes; server-side checks stop malicious
requests (curl, scripts, bots). Never trust the client — standard security
rule.

**31. What is a 400 vs 405 response in your API?**
400 = Bad Request (malformed JSON or invalid email); 405 = Method Not Allowed
(e.g. GET on a POST-only endpoint).

**32. Explain the checker module structure.**
`WHITELIST` — trusted domains; `SUSPICIOUS_TLDS`, `LOOKALIKE_MAP`,
`URGENCY_KEYWORDS` — rule tables; `_heuristic_score()` — computes score +
reasons; `check_email()` — the orchestrator returning a dict result.

**33. Why return a dict instead of a string?**
Structured data (status, color, reports, reasons, source) lets both the GUI
and the web UI use one engine, and reasons give users an explainable verdict.

---

## D. FRONTEND / BACKEND / DEPLOYMENT

**34. What did you use for the web frontend?**
Plain HTML5 + CSS3 (dark cyber theme) + vanilla JavaScript fetch() — no
framework, so it teaches fundamentals and stays fast. It's a responsive
single-page experience.

**35. What did you use for the backend?**
Python **Flask** (WSGI). One `app.py` serves the static frontend and the JSON
API. Same engine modules as the desktop, i.e. one codebase, two frontends.

**36. Which Flask endpoints did you create?**
POST /api/check, POST /api/report, GET /api/stats, GET /api/threats,
GET /api/health — plus static '/' service.

**37. What is WSGI?**
Web Server Gateway Interface — a Python standard that lets servers (gunicorn,
Vercel's runtime) call application objects like Flask's `app` with a standard
environ. It's the bridge hosting servers use to run Python web apps.

**38. Where is it deployed and how?**
On Vercel, using the @vercel/python builder: `vercel.json` routes every URL
to `app.py`, Flask handles routing. Deployed via `npx vercel deploy --prod`.
Live URL: https://phishing-shield-navy.vercel.app

**39. Why serverless?**
No server maintenance, scales to zero when unused (free tier), automatic
HTTPS, and per-request isolation. Ideal for a student project API.

**40. What is the difference between your desktop app and web app?**
Desktop = offline, clipboard monitoring, Tkinter UI, local files.
Web = hosted, browser access, same engine, plus public API. Together they're
the full-stack version of one idea.

**41. CORS — what is it and did you need it?**
Cross-Origin Resource Sharing — browsers block JS calling other origins
unless the server allows it. My standalone `server.py` demo API sends
`Access-Control-Allow-Origin: *` so the local frontend can call it.

---

## E. CYBERSECURITY CONCEPT QUESTIONS

**42. What are the main types of phishing?**
Email phishing (mass), spear phishing (targeted person), whaling (CEOs), and
smishing (SMS), vishing (voice). Mine targets email/spear variants.

**43. What social-engineering tricks do phishers use?**
Urgency & fear (account suspension), authority (RBI, income tax), reward
bias (lottery, refund), and familiarity (brand logos, look-alike domains) —
my keyword and look-alike rules encode exactly these four.

**44. How do fake domains mimic real ones?**
Typosquatting (paypa1.com), subdomain abuse (sbi.co.in.verify-safe.xyz),
wrong TLD choice, homoglyphs. Checking domain reputation + lexical rules
catches most of these.

**45. What should a user NEVER share over email?**
Passwords, OTPs, CVV, full card numbers, PAN/Aadhaar. No legitimate bank or
software company ever asks by email — that's the golden rule.

**46. If you get a phishing email, what are the right steps?**
Don't click links or open attachments; don't reply; report it (in Gmail:
Report phishing); block the sender; if you already clicked — change that
password, enable 2FA, and inform the bank immediately.

**47. What is a zero-day phishing attack?**
A scam using a brand-new domain that no blacklist has seen yet. My heuristic
layer is designed precisely for this class of attack.

---

## F. ADVANCED / EXTRAS YOUR EXAMINER MAY ASK

**48. Limitations of your project?**
Community data starts small (needs adoption), heuristics can produce rare
false positives (mitigated by the whitelist), no ML yet, and the community
DB is per-device (central sync is future scope).

**49. How would you add machine learning?**
Extract features (domain entropy, age of domain, TLD risk, keyword counts,
SPF/DKIM results) and train Naive Bayes / Random Forest on labelled datasets
(UCI/Kaggle phishing corpora), then replace the rule score with the model's
probability while keeping the whitelist as a hard override.

**50. Why should you get good marks for this project? 🙂**
Real working software (not a slide), a novel 3-layer detection design, a
crash-fixed production backend, a live public deployment with an open API,
screenshots and reproducible build steps, plus documents (report, README,
viva Q&A) — it demonstrates end-to-end engineering, security thinking and
community-based innovation.

---

### 💡 Quick-fire numbers to remember in viva
- Threshold: **10 reports = PHISHING**, 1–9 = SUSPICIOUS
- Rate limit: **1 report / device / email / day**
- Clipboard poll: **every 1 second**, GUI pump: **250 ms**
- Heuristic weights: TLD +2, look-alike +3, brand +1, keywords +1 (max +2), numeric +1; **score ≥ 3 = PHISHING**
- DB: **65 seeded entries**, 1,500+ reports
- Live URL: **https://phishing-shield-navy.vercel.app**
- Login: **admin / admin123**
