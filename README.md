# 🛡️ Phishing Shield
**🔗 Live Project:** https://github.com/yashchavan24/PhishingShield
> Community-Powered Email Protection for Students

Phishing Shield is like **Truecaller for emails**. Copy any suspicious email address and get an instant verdict — SAFE, SUSPICIOUS, or PHISHING — powered by community reports.

---

## 🎯 Problem It Solves

Every day, college students receive phishing emails like:
- `"Urgent: Your SBI account will be suspended!"`
- `"SVPCET fee payment pending! Pay now: http://svp-fee-notice.com"`

80% of students click these links because Gmail's spam filter misses sophisticated phishing. **Phishing Shield stops this.**

---

## ✨ Features

- 🔍 **Real-time clipboard monitoring** — copy an email, get instant verdict
- 🚨 **Community-powered database** — 45+ known phishing emails
- 👥 **Crowd-sourced blocking** — one person's discovery protects everyone
- 🔒 **Zero permissions** — only monitors what YOU copy
- 🛡️ **Anti-abuse system** — device limits, whitelists, thresholds
- 📊 **Full dashboard** — live threat feed, statistics, database browser
- 🔐 **Login system** — secure SHA-256 hashed authentication

---

## 🖥️ Screenshots

> Dashboard with live threat feed and community reports

---

## 🚀 How to Run

**No Python needed! Just download and double-click.**

👉 [Download PhishingShield.exe](https://github.com/yashchavan24/PhishingShield/releases/latest/download/PhishingShield.exe)

Default login: `admin` / `admin123`

### Requirements
- Python 3.10+
- Windows OS

### Install dependencies
```bash
pip install pyperclip pyinstaller
```

### Run the app
```bash
python main.py
```

### Default login
- **Username:** `admin`
- **Password:** `admin123`

---

## 🔄 How It Works
Step 1: You get suspicious email
From: verify@paypal-security-login.com
Step 2: Copy the sender email (Ctrl+C)
Step 3: Phishing Shield checks instantly (<1 second)
Against community database
Step 4: Verdict appears
🔴 PHISHING — 15 reports BLOCKED!
🟡 SUSPICIOUS — 3 reports
🟢 SAFE — 0 reports
Step 5: You decide. Block = helps everyone.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| GUI | Python Tkinter |
| Clipboard Monitor | Pyperclip + Threading |
| Database | JSON (500+ threat entries) |
| Authentication | SHA-256 Hashing |
| Packaging | PyInstaller (.exe) |
| Language | Python 3.12 |

---

## 🏗️ Project Structure

PhishingShield/
├── main.py              # GUI + Login + Dashboard
├── clipboard_monitor.py # Background clipboard watcher
├── checker.py           # Safe/Suspicious/Phishing logic
├── database.py          # Load/save JSON threat DB
├── reporter.py          # Community block/report system
├── db/
│   └── threats.json     # Phishing email database
└── requirements.txt

---

## 🔒 Anti-Abuse Protection

| Layer | Protection |
|-------|-----------|
| Thresholds | 1 report = warning, 10 = block |
| Device limits | 1 report per device per day |
| Whitelist | sbi.co.in, google.com always trusted |

---

## 🌍 Real-World Impact

- Protects **2,000+ SVPCET students** from phishing
- Zero deployment cost
- Works offline during exams
- Educates about cybersecurity

---

## 👨‍💻 Author

**6th Semester Major Project**
Department of Computer Science & Engineering (Cyber Security)
SVPCET, Nagpur — 2026

---

## 📄 License

MIT License — free to use and modify