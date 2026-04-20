import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
from datetime import datetime
import hashlib
import json
import os
import sys
import math

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from clipboard_monitor import ClipboardMonitor
from checker import check_email, is_email
from reporter import report_email
from database import get_stats, load_db

USERS_FILE = os.path.join(BASE_DIR, "users.json")

def load_users():
    if not os.path.exists(USERS_FILE):
        default = {"admin": hashlib.sha256("admin123".encode()).hexdigest()}
        with open(USERS_FILE, "w") as f:
            json.dump(default, f)
        return default
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ── PALETTE ───────────────────────────────────────────────────────────────────
BG          = "#070b14"
BG2         = "#0d1321"
BG3         = "#111827"
CARD        = "#0f172a"
CARD2       = "#131f35"
BORDER      = "#1e3a5f"
BORDER2     = "#0ea5e9"

CYAN        = "#06b6d4"
CYAN2       = "#0891b2"
PURPLE      = "#8b5cf6"
PURPLE2     = "#7c3aed"
PINK        = "#ec4899"
ORANGE      = "#f97316"
GREEN       = "#10b981"
GREEN2      = "#059669"
RED         = "#ef4444"
RED2        = "#dc2626"
YELLOW      = "#f59e0b"
BLUE        = "#3b82f6"

TXT1        = "#f1f5f9"
TXT2        = "#94a3b8"
TXT3        = "#475569"

F_TITLE     = ("Segoe UI", 24, "bold")
F_HEAD      = ("Segoe UI", 12, "bold")
F_BODY      = ("Segoe UI", 10)
F_SMALL     = ("Segoe UI", 9)
F_MONO      = ("Consolas", 10)
F_MONO_S    = ("Consolas", 9)
F_NAV       = ("Segoe UI", 10, "bold")

# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN
# ══════════════════════════════════════════════════════════════════════════════
class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.mode = "login"
        self._build()

    def _build(self):
        self.root.title("Phishing Shield")
        self.root.configure(bg=BG)
        self.root.state("zoomed")

        left = tk.Frame(self.root, bg=BG2, width=480)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        self._draw_deco(left)

        right = tk.Frame(self.root, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        center = tk.Frame(right, bg=BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        badge = tk.Frame(center, bg=CARD, highlightbackground=BORDER2,
                         highlightthickness=1)
        badge.pack(pady=(0, 28), ipadx=12, ipady=6)
        tk.Label(badge, text="⬤  SECURE ACCESS PORTAL",
                 font=("Segoe UI", 8, "bold"), fg=CYAN, bg=CARD).pack()

        tk.Label(center, text="Welcome Back",
                 font=("Segoe UI", 32, "bold"), fg=TXT1, bg=BG).pack(anchor="w")
        tk.Label(center, text="Sign in to your Phishing Shield account",
                 font=F_BODY, fg=TXT2, bg=BG).pack(anchor="w", pady=(4, 28))

        tab_frame = tk.Frame(center, bg=BG3, highlightbackground=BORDER,
                             highlightthickness=1)
        tab_frame.pack(fill="x", pady=(0, 20))
        self.tab_login = tk.Button(tab_frame, text="Login",
                                   font=F_NAV, fg=BG, bg=CYAN,
                                   relief="flat", pady=10, padx=40,
                                   cursor="hand2",
                                   command=lambda: self._switch("login"))
        self.tab_login.pack(side="left", fill="x", expand=True)
        self.tab_reg = tk.Button(tab_frame, text="Register",
                                 font=F_NAV, fg=TXT2, bg=BG3,
                                 relief="flat", pady=10, padx=40,
                                 cursor="hand2",
                                 command=lambda: self._switch("register"))
        self.tab_reg.pack(side="left", fill="x", expand=True)

        tk.Label(center, text="Username", font=F_SMALL, fg=TXT2,
                 bg=BG, anchor="w").pack(fill="x", pady=(8, 3))
        self.usr_var = tk.StringVar()
        self._entry(center, self.usr_var)

        tk.Label(center, text="Password", font=F_SMALL, fg=TXT2,
                 bg=BG, anchor="w").pack(fill="x", pady=(12, 3))
        self.pw_var = tk.StringVar()
        self._entry(center, self.pw_var, show="●")

        self.confirm_lbl = tk.Label(center, text="Confirm Password",
                                    font=F_SMALL, fg=TXT2, bg=BG, anchor="w")
        self.cpw_var = tk.StringVar()
        self.confirm_entry = self._entry(center, self.cpw_var, show="●", pack=False)

        self.msg_var = tk.StringVar()
        tk.Label(center, textvariable=self.msg_var,
                 font=F_SMALL, fg=RED, bg=BG).pack(anchor="w", pady=(6, 0))

        self.submit_btn = tk.Button(center, text="LOGIN  →",
                                    font=("Segoe UI", 11, "bold"),
                                    fg=BG, bg=CYAN, relief="flat",
                                    pady=13, cursor="hand2",
                                    command=self._submit)
        self.submit_btn.pack(fill="x", pady=(14, 0))
        self.submit_btn.bind("<Enter>", lambda e: self.submit_btn.config(bg=CYAN2))
        self.submit_btn.bind("<Leave>", lambda e: self.submit_btn.config(bg=CYAN))

        self._switch("login")
        self.root.bind("<Return>", lambda e: self._submit())

    def _draw_deco(self, parent):
        cv = tk.Canvas(parent, bg=BG2, bd=0, highlightthickness=0)
        cv.pack(fill="both", expand=True)

        def draw():
            cv.delete("all")
            w = cv.winfo_width() or 480
            h = cv.winfo_height() or 900
            for i in range(0, w, 40):
                cv.create_line(i, 0, i, h, fill="#0d1f3c", width=1)
            for i in range(0, h, 40):
                cv.create_line(0, i, w, i, fill="#0d1f3c", width=1)
            for cx, cy, r, col in [(240,200,160,CYAN),(80,520,110,PURPLE),(380,680,90,PINK)]:
                for ring in range(3, 0, -1):
                    cv.create_oval(cx-r-ring*14, cy-r-ring*14,
                                   cx+r+ring*14, cy+r+ring*14,
                                   outline=col, width=1)
            cv.create_text(w//2, h//2-90, text="🛡",
                           font=("Segoe UI", 68), fill=CYAN)
            cv.create_text(w//2, h//2+10, text="PHISHING SHIELD",
                           font=("Segoe UI", 18, "bold"), fill=TXT1)
            cv.create_text(w//2, h//2+40, text="Community-Powered Protection",
                           font=("Segoe UI", 10), fill=TXT2)
            bx = w//4
            for val, lbl in [("45+","Threats"),("1191","Reports"),("100%","Free")]:
                cv.create_text(bx, h-90, text=val,
                               font=("Segoe UI", 16, "bold"), fill=CYAN)
                cv.create_text(bx, h-68, text=lbl,
                               font=("Segoe UI", 9), fill=TXT2)
                bx += w//4

        parent.after(150, draw)
        cv.bind("<Configure>", lambda e: draw())

    def _entry(self, parent, var, show="", pack=True):
        e = tk.Entry(parent, textvariable=var, font=F_MONO,
                     fg=TXT1, bg=BG3, insertbackground=CYAN,
                     relief="flat", bd=0, show=show, width=34)
        e.configure(highlightthickness=1,
                    highlightbackground=BORDER, highlightcolor=CYAN2)
        if pack:
            e.pack(fill="x", ipady=10)
        return e

    def _switch(self, mode):
        self.mode = mode
        if mode == "login":
            self.tab_login.config(fg=BG, bg=CYAN)
            self.tab_reg.config(fg=TXT2, bg=BG3)
            self.confirm_lbl.pack_forget()
            self.confirm_entry.pack_forget()
            self.submit_btn.config(text="LOGIN  →")
        else:
            self.tab_login.config(fg=TXT2, bg=BG3)
            self.tab_reg.config(fg=BG, bg=CYAN)
            self.confirm_lbl.pack(fill="x", pady=(12, 3))
            self.confirm_entry.pack(fill="x", ipady=10)
            self.submit_btn.config(text="CREATE ACCOUNT  →")
        self.msg_var.set("")

    def _submit(self):
        u = self.usr_var.get().strip()
        p = self.pw_var.get().strip()
        users = load_users()
        if self.mode == "login":
            if u in users and users[u] == hash_pw(p):
                self.on_success(u)
            else:
                self.msg_var.set("❌  Invalid username or password.")
        else:
            cp = self.cpw_var.get().strip()
            if not u or not p:
                self.msg_var.set("❌  Username and password required.")
                return
            if p != cp:
                self.msg_var.set("❌  Passwords do not match.")
                return
            if u in users:
                self.msg_var.set("❌  Username already exists.")
                return
            users[u] = hash_pw(p)
            save_users(users)
            self.msg_var.set("✅  Account created! Please login.")
            self._switch("login")


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
class PhishingShieldApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.monitor = ClipboardMonitor(self.on_email_detected)
        self.is_monitoring = False
        self.scan_count = 0
        self.blocked_count = 0
        self.root.title("Phishing Shield — Dashboard")
        self.root.configure(bg=BG)
        self.root.state("zoomed")
        self.root.minsize(1200, 700)
        self._build()

    def _build(self):
        self._topbar()
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)
        self._sidebar(body)
        self.main_area = tk.Frame(body, bg=BG)
        self.main_area.pack(side="left", fill="both", expand=True)
        self._show_dashboard()

    def _topbar(self):
        bar = tk.Frame(self.root, bg=BG2, height=52)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        logo = tk.Frame(bar, bg=BG2)
        logo.pack(side="left", padx=20)
        tk.Label(logo, text="🛡", font=("Segoe UI", 18), fg=CYAN, bg=BG2).pack(side="left")
        tk.Label(logo, text=" PHISHING SHIELD",
                 font=("Segoe UI", 13, "bold"), fg=TXT1, bg=BG2).pack(side="left")

        right = tk.Frame(bar, bg=BG2)
        right.pack(side="right", padx=20)

        self.clock_lbl = tk.Label(right, font=F_SMALL, fg=TXT2, bg=BG2)
        self.clock_lbl.pack(side="right", padx=(16, 0))
        self._tick()

        pill = tk.Frame(right, bg=CARD, highlightbackground=BORDER,
                        highlightthickness=1)
        pill.pack(side="right", ipadx=10, ipady=4)
        tk.Label(pill, text=f"👤  {self.username}",
                 font=F_SMALL, fg=CYAN, bg=CARD).pack()

        self.top_indicator = tk.Label(bar, text="⬤  OFFLINE",
                                      font=("Segoe UI", 9, "bold"),
                                      fg=TXT3, bg=BG2)
        self.top_indicator.pack(side="right", padx=20)

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

    def _tick(self):
        self.clock_lbl.config(text=datetime.now().strftime("%d %b %Y   %H:%M:%S"))
        self.root.after(1000, self._tick)

    def _sidebar(self, parent):
        sb = tk.Frame(parent, bg=BG2, width=210)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        tk.Frame(sb, bg=BORDER, width=1).pack(side="right", fill="y")

        tk.Label(sb, text="MENU", font=("Segoe UI", 8, "bold"),
                 fg=TXT3, bg=BG2).pack(anchor="w", padx=18, pady=(20, 6))

        nav_items = [
            ("dashboard", "⊞", "Dashboard"),
            ("scan",      "⊕", "Manual Scan"),
            ("database",  "≡", "Threat Database"),
            ("stats",     "↗", "Statistics"),
            ("about",     "i", "About"),
        ]
        self.nav_btns = {}
        for key, icon, label in nav_items:
            f = tk.Frame(sb, bg=BG2, cursor="hand2")
            f.pack(fill="x", padx=8, pady=2)
            icon_lbl = tk.Label(f, text=icon, font=("Segoe UI", 12),
                                fg=TXT2, bg=BG2, width=3)
            icon_lbl.pack(side="left")
            lbl = tk.Label(f, text=label, font=F_NAV, fg=TXT2, bg=BG2,
                           anchor="w", pady=10)
            lbl.pack(side="left", fill="x", expand=True)
            accent = tk.Frame(f, bg=BG2, width=3)
            accent.pack(side="right", fill="y")

            def make_click(k):
                return lambda e=None: self._nav_click(k)
            for w in [f, icon_lbl, lbl, accent]:
                w.bind("<Button-1>", make_click(key))
            self.nav_btns[key] = (f, icon_lbl, lbl, accent)

        tk.Frame(sb, bg=BORDER, height=1).pack(fill="x", padx=12, pady=16)
        tk.Label(sb, text="QUICK SCAN", font=("Segoe UI", 8, "bold"),
                 fg=TXT3, bg=BG2).pack(anchor="w", padx=18, pady=(0, 8))

        self.quick_var = tk.StringVar()
        qf = tk.Frame(sb, bg=BG2)
        qf.pack(fill="x", padx=12)
        qe = tk.Entry(qf, textvariable=self.quick_var,
                      font=F_MONO_S, fg=TXT1, bg=BG3,
                      insertbackground=CYAN, relief="flat", bd=0)
        qe.configure(highlightthickness=1,
                     highlightbackground=BORDER, highlightcolor=CYAN)
        qe.pack(fill="x", ipady=7, pady=(0, 6))
        qe.bind("<Return>", lambda e: self._quick_scan())
        tk.Button(qf, text="SCAN →", font=("Segoe UI", 9, "bold"),
                  fg=BG, bg=CYAN, relief="flat", pady=8,
                  cursor="hand2", command=self._quick_scan).pack(fill="x")

        tk.Frame(sb, bg=BORDER, height=1).pack(fill="x", padx=12, pady=16)
        self.mon_btn = tk.Button(sb, text="▶  START MONITORING",
                                 font=("Segoe UI", 9, "bold"),
                                 fg=BG, bg=GREEN, relief="flat", pady=10,
                                 cursor="hand2", command=self.toggle_monitoring)
        self.mon_btn.pack(fill="x", padx=12, pady=(0, 16))

        self._nav_click("dashboard")

    def _nav_click(self, key):
        for k, (f, icon_lbl, lbl, accent) in self.nav_btns.items():
            if k == key:
                f.config(bg=CARD); icon_lbl.config(fg=CYAN, bg=CARD)
                lbl.config(fg=CYAN, bg=CARD); accent.config(bg=CYAN)
            else:
                f.config(bg=BG2); icon_lbl.config(fg=TXT2, bg=BG2)
                lbl.config(fg=TXT2, bg=BG2); accent.config(bg=BG2)
        views = {
            "dashboard": self._show_dashboard,
            "scan":      self._show_manual,
            "database":  self._show_database,
            "stats":     self._show_stats,
            "about":     self._show_about,
        }
        if hasattr(self, "main_area"):
            views[key]()

    def _clear_main(self):
        for w in self.main_area.winfo_children():
            w.destroy()

    def _scrollable(self):
        cv = tk.Canvas(self.main_area, bg=BG, bd=0, highlightthickness=0)
        vsb = tk.Scrollbar(self.main_area, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(cv, bg=BG)
        cv.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<MouseWheel>",
                lambda e: cv.yview_scroll(int(-1*(e.delta/120)), "units"))
        return inner

    # ── DASHBOARD ─────────────────────────────────────────────────────────────
    def _show_dashboard(self):
        self._clear_main()
        p = self._scrollable()

        hrow = tk.Frame(p, bg=BG)
        hrow.pack(fill="x", padx=28, pady=(24, 0))
        tk.Label(hrow, text="Dashboard", font=F_TITLE, fg=TXT1, bg=BG).pack(side="left")
        tk.Label(hrow, text=f"  {datetime.now().strftime('%A, %d %B %Y')}",
                 font=F_BODY, fg=TXT2, bg=BG).pack(side="left", pady=(8, 0))

        total_r, confirmed = get_stats()
        db = load_db()
        suspicious_count = sum(1 for v in db.values() if 1 <= v["reports"] < 10)

        cards = [
            ("Total in DB",    len(db),           CYAN,   "📋"),
            ("Reports",        total_r,            YELLOW, "📢"),
            ("Phishing",       confirmed,          RED,    "🚨"),
            ("Suspicious",     suspicious_count,   ORANGE, "⚠"),
            ("Session Scans",  self.scan_count,    GREEN,  "🔍"),
            ("Session Blocks", self.blocked_count, PURPLE, "🛡"),
        ]
        grid = tk.Frame(p, bg=BG)
        grid.pack(fill="x", padx=28, pady=(16, 0))
        self.stat_labels = {}
        for i, (title, val, color, icon) in enumerate(cards):
            card = tk.Frame(grid, bg=CARD,
                            highlightbackground=BORDER, highlightthickness=1)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            grid.columnconfigure(i, weight=1)
            tk.Frame(card, bg=color, height=3).pack(fill="x")
            inner = tk.Frame(card, bg=CARD)
            inner.pack(fill="both", padx=16, pady=12)
            tk.Label(inner, text=icon, font=("Segoe UI", 14),
                     fg=color, bg=CARD).pack(anchor="w")
            lbl = tk.Label(inner, text=str(val),
                           font=("Segoe UI", 26, "bold"), fg=color, bg=CARD)
            lbl.pack(anchor="w", pady=(4, 0))
            tk.Label(inner, text=title, font=F_SMALL, fg=TXT2, bg=CARD).pack(anchor="w")
            self.stat_labels[title] = lbl

        content = tk.Frame(p, bg=BG)
        content.pack(fill="both", expand=True, padx=28, pady=16)

        # live feed
        feed_card = tk.Frame(content, bg=CARD,
                             highlightbackground=BORDER, highlightthickness=1)
        feed_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        feed_hdr = tk.Frame(feed_card, bg=CARD2)
        feed_hdr.pack(fill="x")
        tk.Frame(feed_card, bg=CYAN, height=2).pack(fill="x")
        tk.Label(feed_hdr, text="  📡  Live Threat Feed",
                 font=F_HEAD, fg=TXT1, bg=CARD2).pack(side="left", pady=10)
        tk.Button(feed_hdr, text="Clear",
                  font=F_SMALL, fg=TXT2, bg=CARD2, relief="flat",
                  cursor="hand2", command=self._clear_log).pack(side="right", padx=10)

        self.log = scrolledtext.ScrolledText(
            feed_card, height=20, font=F_MONO,
            bg="#050810", fg=TXT1, insertbackground="white",
            relief="flat", padx=14, pady=12, state="disabled")
        self.log.pack(fill="both", expand=True, padx=4, pady=4)
        self.log.tag_config("phishing",   foreground=RED)
        self.log.tag_config("suspicious", foreground=YELLOW)
        self.log.tag_config("safe",       foreground=GREEN)
        self.log.tag_config("info",       foreground=TXT2)
        self.log.tag_config("time",       foreground=TXT3)
        self.log.tag_config("block",      foreground=PURPLE)
        self._log("System ready. Click START MONITORING or use Quick Scan.", "info")

        # right panel
        rp = tk.Frame(content, bg=BG, width=300)
        rp.pack(side="left", fill="y")
        rp.pack_propagate(False)

        tc = tk.Frame(rp, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        tc.pack(fill="x", pady=(0, 10))
        tk.Frame(tc, bg=RED, height=2).pack(fill="x")
        tk.Label(tc, text="  🔥  Top Threats",
                 font=F_HEAD, fg=TXT1, bg=CARD2).pack(anchor="w", pady=8)
        tk.Frame(tc, bg=BORDER, height=1).pack(fill="x", padx=10)

        db2 = load_db()
        threats = sorted(
            [(k, v) for k, v in db2.items() if v["reports"] > 0],
            key=lambda x: x[1]["reports"], reverse=True)[:10]
        for email, data in threats:
            r = data["reports"]
            col = RED if r >= 10 else YELLOW
            row = tk.Frame(tc, bg=CARD)
            row.pack(fill="x", padx=10, pady=3)
            short = email[:26] + "…" if len(email) > 26 else email
            tk.Label(row, text=short, font=F_MONO_S,
                     fg=TXT1, bg=CARD, anchor="w").pack(side="left")
            pill = tk.Frame(row, bg=col)
            pill.pack(side="right")
            tk.Label(pill, text=f" {r} ", font=("Segoe UI", 8, "bold"),
                     fg=BG, bg=col).pack()

        ac = tk.Frame(rp, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        ac.pack(fill="x")
        tk.Frame(ac, bg=PURPLE, height=2).pack(fill="x")
        tk.Label(ac, text="  ⚡  Quick Actions",
                 font=F_HEAD, fg=TXT1, bg=CARD2).pack(anchor="w", pady=8)
        for txt, key, col in [
            ("Open Threat Database →", "database", CYAN),
            ("Run Manual Scan →",      "scan",     GREEN),
            ("View Statistics →",      "stats",    PURPLE),
        ]:
            tk.Button(ac, text=txt, font=F_SMALL, fg=col, bg=CARD,
                      relief="flat", anchor="w", padx=10, pady=6,
                      cursor="hand2",
                      command=lambda k=key: self._nav_click(k)).pack(fill="x")
        tk.Label(ac, text="", bg=CARD).pack()

    # ── DATABASE ──────────────────────────────────────────────────────────────
    def _show_database(self):
        self._clear_main()
        p = self.main_area

        hdr = tk.Frame(p, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(24, 10))
        tk.Label(hdr, text="Threat Database", font=F_TITLE,
                 fg=TXT1, bg=BG).pack(side="left")

        ctrl = tk.Frame(p, bg=BG)
        ctrl.pack(fill="x", padx=28, pady=(0, 10))
        self.search_var = tk.StringVar()
        sf = tk.Frame(ctrl, bg=BG3, highlightbackground=CYAN, highlightthickness=1)
        sf.pack(side="left")
        tk.Label(sf, text="  🔍 ", font=F_BODY, fg=CYAN, bg=BG3).pack(side="left")
        tk.Entry(sf, textvariable=self.search_var, font=F_MONO_S,
                 fg=TXT1, bg=BG3, insertbackground=CYAN,
                 relief="flat", bd=0, width=28).pack(side="left", ipady=8, padx=(0, 10))
        self.search_var.trace("w", lambda *a: self._refresh_db_table())

        self.filter_var = tk.StringVar(value="All")
        for label, col in [("All",TXT1),("Phishing",RED),("Suspicious",YELLOW),("Safe",GREEN)]:
            tk.Button(ctrl, text=label, font=F_SMALL, fg=col, bg=CARD,
                      relief="flat", padx=14, pady=8, cursor="hand2",
                      command=lambda l=label: self._set_filter(l)).pack(side="left", padx=4)

        tf = tk.Frame(p, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        tf.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("PS.Treeview",
                        background=CARD, fieldbackground=CARD,
                        foreground=TXT1, font=F_MONO_S, rowheight=30)
        style.configure("PS.Treeview.Heading",
                        background=BG2, foreground=CYAN,
                        font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("PS.Treeview",
                  background=[("selected", CARD2)],
                  foreground=[("selected", CYAN)])

        cols = ("Email Address", "Status", "Reports", "Category", "First Seen")
        self.tree = ttk.Treeview(tf, columns=cols, show="headings", style="PS.Treeview")
        for col, w in zip(cols, [360, 120, 80, 130, 110]):
            self.tree.heading(col, text=col,
                              command=lambda c=col: self._sort_tree(c))
            self.tree.column(col, width=w, anchor="w")
        vsb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self._refresh_db_table()

    def _set_filter(self, val):
        self.filter_var.set(val)
        self._refresh_db_table()

    def _refresh_db_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        db = load_db()
        q    = self.search_var.get().lower()
        filt = self.filter_var.get()
        for email, data in db.items():
            r = data["reports"]
            status = "PHISHING" if r >= 10 else ("SUSPICIOUS" if r >= 1 else "SAFE")
            if filt != "All" and status != filt.upper():
                continue
            if q and q not in email.lower():
                continue
            self.tree.insert("", "end",
                             values=(email, status, r,
                                     data.get("category","Unknown"),
                                     data.get("first_seen","—")),
                             tags=(status.lower(),))
        self.tree.tag_configure("phishing",   foreground=RED)
        self.tree.tag_configure("suspicious", foreground=YELLOW)
        self.tree.tag_configure("safe",       foreground=GREEN)

    def _sort_tree(self, col):
        data = [(self.tree.set(c, col), c) for c in self.tree.get_children("")]
        try:    data.sort(key=lambda x: int(x[0]))
        except: data.sort()
        for i, (_, c) in enumerate(data):
            self.tree.move(c, "", i)

    # ── STATS ─────────────────────────────────────────────────────────────────
    def _show_stats(self):
        self._clear_main()
        p = self._scrollable()
        tk.Label(p, text="Statistics", font=F_TITLE,
                 fg=TXT1, bg=BG).pack(anchor="w", padx=28, pady=(24, 16))

        db = load_db()
        cats, sc = {}, {"PHISHING": 0, "SUSPICIOUS": 0, "SAFE": 0}
        for data in db.values():
            r = data["reports"]
            cat = data.get("category", "Unknown")
            cats[cat] = cats.get(cat, 0) + 1
            if r >= 10:  sc["PHISHING"] += 1
            elif r >= 1: sc["SUSPICIOUS"] += 1
            else:        sc["SAFE"] += 1

        card = self._card(p, "Threat Status Breakdown", CYAN)
        total = sum(sc.values()) or 1
        for label, col in [("PHISHING",RED),("SUSPICIOUS",YELLOW),("SAFE",GREEN)]:
            cnt = sc[label]
            pct = cnt / total
            row = tk.Frame(card, bg=CARD)
            row.pack(fill="x", padx=16, pady=5)
            tk.Label(row, text=f"{label:<12}", font=F_MONO_S,
                     fg=col, bg=CARD, width=13, anchor="w").pack(side="left")
            bg_bar = tk.Frame(row, bg=BG3, height=18)
            bg_bar.pack(side="left", fill="x", expand=True)
            bg_bar.update_idletasks()
            tk.Frame(bg_bar, bg=col, height=18,
                     width=max(4, int(pct*500))).place(x=0, y=0)
            tk.Label(row, text=f"  {cnt}  ({pct*100:.0f}%)",
                     font=F_SMALL, fg=TXT2, bg=CARD, width=14).pack(side="left")
        tk.Label(card, text="", bg=CARD).pack()

        card2 = self._card(p, "Threats by Category", PURPLE)
        cg = tk.Frame(card2, bg=CARD)
        cg.pack(fill="x", padx=16, pady=(4, 16))
        pal = [CYAN, PURPLE, RED, YELLOW, GREEN, ORANGE, PINK, BLUE]
        for i, (cat, cnt) in enumerate(sorted(cats.items(), key=lambda x: -x[1])):
            col = pal[i % len(pal)]
            box = tk.Frame(cg, bg=BG3, highlightbackground=col, highlightthickness=1)
            box.grid(row=i//4, column=i%4, padx=8, pady=8,
                     ipadx=16, ipady=10, sticky="nsew")
            cg.columnconfigure(i%4, weight=1)
            tk.Label(box, text=str(cnt),
                     font=("Segoe UI", 22, "bold"), fg=col, bg=BG3).pack()
            tk.Label(box, text=cat, font=F_SMALL, fg=TXT2, bg=BG3).pack()

        card3 = self._card(p, "Most Reported Emails", RED)
        top5 = sorted(db.items(), key=lambda x: x[1]["reports"], reverse=True)[:5]
        for rank, (email, data) in enumerate(top5, 1):
            r = data["reports"]
            row = tk.Frame(card3, bg=CARD)
            row.pack(fill="x", padx=16, pady=4)
            tk.Label(row, text=f"#{rank}", font=("Segoe UI", 11, "bold"),
                     fg=TXT3, bg=CARD, width=3).pack(side="left")
            tk.Label(row, text=email, font=F_MONO_S,
                     fg=TXT1, bg=CARD).pack(side="left", padx=8)
            tk.Label(row, text=f"{r} reports", font=F_SMALL,
                     fg=RED, bg=CARD).pack(side="right")
        tk.Label(card3, text="", bg=CARD).pack()

    def _card(self, parent, title, accent):
        outer = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        outer.pack(fill="x", padx=28, pady=(0, 14))
        tk.Frame(outer, bg=accent, height=2).pack(fill="x")
        tk.Label(outer, text=f"  {title}", font=F_HEAD, fg=TXT1, bg=CARD2).pack(anchor="w", pady=10)
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", padx=10)
        return outer

    # ── MANUAL SCAN ───────────────────────────────────────────────────────────
    def _show_manual(self):
        self._clear_main()
        p = self.main_area
        tk.Label(p, text="Manual Scan", font=F_TITLE,
                 fg=TXT1, bg=BG).pack(anchor="w", padx=28, pady=(24, 4))
        tk.Label(p, text="Enter any email address to check it against the community database.",
                 font=F_BODY, fg=TXT2, bg=BG).pack(anchor="w", padx=28, pady=(0, 20))

        card = tk.Frame(p, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.pack(padx=28, fill="x")
        tk.Frame(card, bg=CYAN, height=2).pack(fill="x")
        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill="x", padx=24, pady=24)

        tk.Label(inner, text="Email Address", font=F_SMALL, fg=TXT2, bg=CARD).pack(anchor="w")
        ms_var = tk.StringVar()
        ef = tk.Frame(inner, bg=BG3, highlightbackground=CYAN, highlightthickness=1)
        ef.pack(fill="x", pady=(6, 16))
        tk.Label(ef, text="  @  ", font=F_BODY, fg=CYAN, bg=BG3).pack(side="left")
        me = tk.Entry(ef, textvariable=ms_var, font=("Consolas", 13),
                      fg=TXT1, bg=BG3, insertbackground=CYAN,
                      relief="flat", bd=0)
        me.pack(side="left", fill="x", expand=True, ipady=12, padx=(0, 10))
        me.focus()

        result_frame = tk.Frame(card, bg=CARD)
        result_frame.pack(fill="x", padx=24, pady=(0, 24))

        def do_scan():
            email = ms_var.get().strip()
            if not is_email(email):
                messagebox.showerror("Invalid", "Please enter a valid email address.")
                return
            res = check_email(email)
            for w in result_frame.winfo_children():
                w.destroy()
            color, status, reports = res["color"], res["status"], res["reports"]
            rc = tk.Frame(result_frame, bg=BG3,
                          highlightbackground=color, highlightthickness=2)
            rc.pack(fill="x", pady=(0, 10))
            tk.Frame(rc, bg=color, height=4).pack(fill="x")
            ri = tk.Frame(rc, bg=BG3)
            ri.pack(fill="x", padx=20, pady=16)
            tk.Label(ri, text=status, font=("Segoe UI", 20, "bold"),
                     fg=color, bg=BG3).pack(anchor="w")
            tk.Label(ri, text=email, font=F_MONO, fg=TXT1, bg=BG3).pack(anchor="w", pady=(4, 0))
            tk.Label(ri, text=f"Community reports: {reports}",
                     font=F_SMALL, fg=TXT2, bg=BG3).pack(anchor="w")
            if reports >= 1:
                tk.Button(ri, text="🚫  BLOCK & REPORT",
                          font=("Segoe UI", 10, "bold"),
                          fg=BG, bg=RED, relief="flat", padx=16, pady=8,
                          cursor="hand2",
                          command=lambda: self._do_block(email)).pack(anchor="w", pady=(12, 0))
            self._log(f"{email}  →  {status}  ({reports} reports)",
                      "phishing" if "PHISHING" in status else
                      ("suspicious" if "SUSPICIOUS" in status else "safe"))
            self.scan_count += 1
            self._update_stats()

        me.bind("<Return>", lambda e: do_scan())
        tk.Button(inner, text="SCAN EMAIL  →",
                  font=("Segoe UI", 11, "bold"), fg=BG, bg=CYAN,
                  relief="flat", pady=12, cursor="hand2",
                  command=do_scan).pack(fill="x")

    # ── ABOUT ─────────────────────────────────────────────────────────────────
    def _show_about(self):
        self._clear_main()
        p = self._scrollable()
        tk.Label(p, text="About", font=F_TITLE,
                 fg=TXT1, bg=BG).pack(anchor="w", padx=28, pady=(24, 16))

        for col, title, body in [
            (CYAN,   "🛡  What is Phishing Shield?",
             "Phishing Shield is like Truecaller for emails. Copy a suspicious sender's\n"
             "address and get an instant community-powered verdict in under 1 second."),
            (GREEN,  "⚙  How It Works",
             "The clipboard monitor runs silently in the background, checking every second.\n"
             "It cross-references copied emails with the community threat database instantly."),
            (PURPLE, "🔒  Privacy & Ethics",
             "Zero email-read permissions. Only sees what you copy. No personal data collected.\n"
             "Report counts are anonymous and shared to protect the entire community."),
            (ORANGE, "🚀  Tech Stack",
             "Python 3.12  ·  Tkinter GUI  ·  Pyperclip  ·  Threading\n"
             "JSON Database  ·  SHA-256 Auth  ·  PyInstaller (.exe)"),
            (YELLOW, "🎯  Future Roadmap",
             "Gmail API integration  ·  Browser extension  ·  ML-based detection\n"
             "College network deployment  ·  National student protection network"),
        ]:
            card = tk.Frame(p, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
            card.pack(fill="x", padx=28, pady=(0, 12))
            tk.Frame(card, bg=col, height=2).pack(fill="x")
            tk.Label(card, text=f"  {title}", font=F_HEAD,
                     fg=col, bg=CARD2).pack(anchor="w", pady=(10, 6))
            tk.Label(card, text=body, font=F_BODY,
                     fg=TXT1, bg=CARD, justify="left").pack(anchor="w", padx=16, pady=(0, 14))

        tk.Label(p, text="Phishing Shield v2.0  ·  6th Sem Major Project  ·  SVPCET",
                 font=F_SMALL, fg=TXT3, bg=BG).pack(pady=10)

    # ── HELPERS ───────────────────────────────────────────────────────────────
    def _log(self, msg, tag="info"):
        if not hasattr(self, "log") or not self.log.winfo_exists():
            return
        self.log.configure(state="normal")
        self.log.insert("end", datetime.now().strftime("[%H:%M:%S] "), "time")
        self.log.insert("end", msg + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        if hasattr(self, "log"):
            self.log.configure(state="normal")
            self.log.delete("1.0", "end")
            self.log.configure(state="disabled")
            self._log("Log cleared.", "info")

    def _update_stats(self):
        if not hasattr(self, "stat_labels"):
            return
        self.stat_labels.get("Session Scans",  tk.Label()).config(text=str(self.scan_count))
        self.stat_labels.get("Session Blocks", tk.Label()).config(text=str(self.blocked_count))

    def toggle_monitoring(self):
        if not self.is_monitoring:
            self.monitor.start()
            self.is_monitoring = True
            self.top_indicator.config(text="⬤  LIVE", fg=GREEN)
            self.mon_btn.config(text="⏹  STOP MONITORING", bg=RED)
            self._log("Clipboard monitoring active. Copy any email!", "safe")
        else:
            self.monitor.stop()
            self.is_monitoring = False
            self.top_indicator.config(text="⬤  OFFLINE", fg=TXT3)
            self.mon_btn.config(text="▶  START MONITORING", bg=GREEN)
            self._log("Monitoring stopped.", "info")

    def on_email_detected(self, result):
        self.root.after(0, self._handle_result, result)

    def _handle_result(self, result):
        self.scan_count += 1
        status, email, reports = result["status"], result["email"], result["reports"]
        tag = ("phishing" if "PHISHING" in status else
               "suspicious" if "SUSPICIOUS" in status else "safe")
        self._log(f"{email}  →  {status}  ({reports} reports)", tag)
        if "PHISHING" in status:
            self._show_alert(result)
        self._update_stats()

    def _quick_scan(self):
        email = self.quick_var.get().strip()
        if not is_email(email):
            return
        self._handle_result(check_email(email))
        self.quick_var.set("")

    def _show_alert(self, result):
        alert = tk.Toplevel(self.root)
        alert.title("PHISHING DETECTED")
        alert.configure(bg=BG)
        alert.grab_set()
        w, h = 480, 320
        sw, sh = alert.winfo_screenwidth(), alert.winfo_screenheight()
        alert.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        tk.Frame(alert, bg=RED, height=4).pack(fill="x")
        inner = tk.Frame(alert, bg=BG)
        inner.pack(fill="both", expand=True, padx=30, pady=24)
        tk.Label(inner, text="🚨  PHISHING DETECTED",
                 font=("Segoe UI", 18, "bold"), fg=RED, bg=BG).pack(anchor="w")
        tk.Label(inner, text=result["email"],
                 font=("Consolas", 11), fg=TXT1, bg=BG).pack(anchor="w", pady=(6, 0))
        r = result["reports"]
        tf = tk.Frame(inner, bg=BG3, height=6)
        tf.pack(fill="x", pady=12)
        tk.Frame(tf, bg=RED, height=6, width=min(r*5, 400)).place(x=0, y=0)
        tk.Label(inner, text=f"Reported {r} times by the community",
                 font=F_SMALL, fg=TXT2, bg=BG).pack(anchor="w")
        tk.Label(inner, text="⚠  DO NOT click any links in this email!",
                 font=("Segoe UI", 10, "bold"), fg=YELLOW, bg=BG).pack(anchor="w", pady=(8, 16))
        btn_row = tk.Frame(inner, bg=BG)
        btn_row.pack(anchor="w")
        tk.Button(btn_row, text="🚫  BLOCK & REPORT",
                  font=("Segoe UI", 10, "bold"), fg=BG, bg=RED,
                  relief="flat", padx=16, pady=9, cursor="hand2",
                  command=lambda: self._do_block(result["email"], alert)).pack(side="left", padx=(0,10))
        tk.Button(btn_row, text="Dismiss",
                  font=F_BODY, fg=TXT2, bg=BG3,
                  relief="flat", padx=16, pady=9, cursor="hand2",
                  command=alert.destroy).pack(side="left")

    def _do_block(self, email, alert_win=None):
        msg = report_email(email)
        self.blocked_count += 1
        self._log(f"BLOCKED: {email}", "block")
        self._update_stats()
        if alert_win:
            alert_win.destroy()
        messagebox.showinfo("Reported", msg, parent=self.root)


# ══════════════════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    root.resizable(True, True)

    def launch(username):
        for w in root.winfo_children():
            w.destroy()
        PhishingShieldApp(root, username)

    LoginWindow(root, launch)
    root.mainloop()

if __name__ == "__main__":
    main()