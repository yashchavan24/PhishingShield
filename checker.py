from database import load_db

WHITELIST = [
    "sbi.co.in", "hdfcbank.com", "icicibank.com",
    "google.com", "microsoft.com", "svpcet.ac.in",
    "gov.in", "edu.in", "amazon.in"
]

def is_email(text):
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(pattern, text.strip()) is not None

def check_email(email: str) -> dict:
    email = email.strip().lower()
    domain = email.split("@")[-1] if "@" in email else ""

    # Whitelist check
    if any(domain == w or domain.endswith("." + w) for w in WHITELIST):
        return {"status": "SAFE", "reports": 0, "color": "#00C851", "email": email}

    db = load_db()
    entry = db.get(email, {"reports": 0, "blocked_by": []})
    count = entry["reports"]

    if count >= 10:
        return {"status": "🚨 PHISHING", "reports": count, "color": "#ff4444", "email": email}
    elif count >= 1:
        return {"status": "⚠️ SUSPICIOUS", "reports": count, "color": "#ffbb33", "email": email}
    else:
        return {"status": "✅ SAFE", "reports": 0, "color": "#00C851", "email": email}