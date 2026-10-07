"""
Phishing Shield — verdict engine.

Three layers of detection, in order:
  1. Whitelist      : verified genuine senders are always SAFE
  2. Community DB   : crowd-sourced report counts (Truecaller model)
  3. Heuristics     : lexical analysis of the address itself
                      (suspicious TLDs, look-alike domains, urgency keywords)
"""
import os
import json
import re

from database import load_db

# Domains (and subdomains of them) that are always trusted
WHITELIST = [
    "sbi.co.in", "sbi.co.in", "onlinesbi.sbi", "hdfcbank.com", "icicibank.com",
    "axisbank.com", "kotak.com", "pnbindia.in", "bankofbaroda.in",
    "unionbankofindia.co.in", "canarabank.com", "centralbankofindia.co.in",
    "google.com", "microsoft.com", "apple.com", "amazon.in", "amazon.com",
    "flipkart.com", "paytm.com", "phonepe.com", "svpcet.ac.in", "gov.in",
    "nic.in", "edu.in", "ac.in", "res.in", "irctc.co.in", "epfindia.gov.in",
    "incometax.gov.in", "uidai.gov.in", "rbi.org.in", "sebi.gov.in",
]

# TLDs commonly abused in phishing (free / cheap / disposable registrars)
SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq",      # free Freenom TLDs
    "top", "xyz", "click", "link", "work", "rest", "surf", "fit",
    "buzz", "monster", "quest", "cyou", "icu", "cam", "sbs",
}

# Single-character substitutions used to fake brand domains (typosquatting)
LOOKALIKE_MAP = {
    "paypa1": "paypal", "paypa1": "paypal", "g00gle": "google",
    "micros0ft": "microsoft", "faceb00k": "facebook", "amaz0n": "amazon",
    "app1e": "apple", "pny": "pay", "secure-sbi": "sbi", "sbi-secure": "sbi",
    "hdfc-bank": "hdfcbank", "icici-bank": "icicibank", "1cicibank": "icicibank",
}

# Urgency / fear keywords that almost always appear in phishing local-parts
URGENCY_KEYWORDS = [
    "verify", "urgent", "suspended", "suspend", "locked", "blocked",
    "confirm", "update-now", "kyc", "alert", "urgent-action", "warning",
    "limited-time", "immediately", "refund", "penalty", "final-notice",
    "account-stop", "login-now", "reactivate", "prize", "winner",
    "lottery", "reward", "claim-now", "secure-update",
]

_EMAIL_RE = re.compile(r"^[\w.!#$%&'*+/=?^_`{|}~-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}$")


def is_email(text):
    """RFC-style lightweight email validation, works with unicode-safe ASCII."""
    if not isinstance(text, str):
        return False
    return _EMAIL_RE.match(text.strip()) is not None


def _heuristic_score(email_address):
    """Return a score >= 0 (0 = clean). Score 2+ means likely phishing."""
    score = 0
    reasons = []
    local, _, domain = email_address.partition("@")

    tld = domain.rsplit(".", 1)[-1].lower()
    if tld in SUSPICIOUS_TLDS:
        score += 2
        reasons.append(f"suspicious TLD .{tld}")

    for bad, good in LOOKALIKE_MAP.items():
        if bad in domain:
            score += 3
            reasons.append(f"impersonates '{good}'")
            break

    brand_parts = ("sbi", "hdfc", "icici", "paypal", "google", "microsoft",
                   "amazon", "paytm", "phonepe", "irctc", "flipkart")
    domain_l = domain.lower()
    if any(b in domain_l for b in brand_parts) and not any(
            domain_l == w or domain_l.endswith("." + w) for w in WHITELIST):
        score += 1
        reasons.append("brand name in unverified domain")

    local_l = local.lower()
    hits = [k for k in URGENCY_KEYWORDS if k in local_l]
    if hits:
        score += min(len(hits), 2)
        reasons.append("urgency keyword: " + ", ".join(hits[:3]))

    digits_only = re.sub(r"\D", "", local)
    if len(digits_only) > 8 and not any(c.isalpha() for c in local):
        score += 1
        reasons.append("mostly-numeric local part")

    return score, reasons


def check_email(email):
    """Full verdict pipeline. Status-only keys keep the desktop GUI working;
    heuristics/reasons add the new intelligence layer for the web UI."""
    email = (email or "").strip().lower()

    domain = email.rpartition("@")[2]

    # 1) Whitelist always wins
    if any(domain == w or domain.endswith("." + w) for w in WHITELIST):
        return {"status": "SAFE", "reports": 0, "color": "#10b981",
                "email": email, "source": "whitelist", "reasons": []}

    # 2) Community database (crowd-sourced reports)
    try:
        db = load_db()
    except Exception:
        db = {}
    entry = db.get(email) if isinstance(db.get(email), dict) else {}
    count = entry.get("reports", 0)
    category = entry.get("category", "Unknown")

    # 3) Heuristic score from the address text itself
    hs, reasons = _heuristic_score(email)

    if count >= 10 or hs >= 3:
        return {"status": "PHISHING", "reports": count, "color": "#ef4444",
                "email": email, "category": category, "heuristics": hs,
                "reasons": reasons,
                "source": ("community" if count >= 10 else "heuristics")}
    if (count >= 1) or (hs >= 1 and count == 0):
        return {"status": "SUSPICIOUS", "reports": count, "color": "#f59e0b",
                "email": email, "category": category, "heuristics": hs,
                "reasons": reasons,
                "source": ("community" if count >= 1 else "heuristics")}
    return {"status": "SAFE", "reports": 0, "color": "#10b981",
            "email": email, "category": category, "heuristics": 0,
            "reasons": [], "source": "database"}


# ── backward-compatible aliases (tests / docs may import these) ──
def check():
    return None
