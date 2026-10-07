/* Phishing Shield — web frontend logic */
(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);

  // ── Scan feature ────────────────────────────────────────────────
  async function scan(email) {
    const box = $("scan-result");
    const btn = $("scan-btn");
    btn.disabled = true;
    btn.textContent = "SCANNING…";
    box.classList.remove("hidden", "safe", "suspicious", "phishing");

    try {
      const res = await fetch("/api/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "scan failed");

      const cls = (data.status || "").toLowerCase().includes("phishing")
        ? "phishing"
        : (data.status || "").toLowerCase().includes("suspicious")
        ? "suspicious"
        : "safe";

      const icon = { phishing: "🚨", suspicious: "⚠️", safe: "✅" }[cls];
      const src =
        data.source === "whitelist"
          ? "Verified sender (whitelist)"
          : data.source === "community"
          ? `Community database · ${data.reports} reports`
          : data.source === "heuristics"
          ? `Heuristic engine · risk score ${data.heuristics}`
          : "No reports in community database";

      box.innerHTML = `
        <div class="badge">${icon} ${data.status}</div>
        <div class="mono" style="font-family:Consolas,monospace;margin-top:6px">${escapeHtml(data.email)}</div>
        <div class="meta-row">
          <span class="pill p-${cls === "phishing" ? "red" : cls === "suspicious" ? "yel" : "grn"}">${escapeHtml(src)}</span>
          ${data.category && data.category !== "Unknown" ? `<span class="pill">${escapeHtml(data.category)}</span>` : ""}
        </div>
        ${data.reasons && data.reasons.length ? `
          <ul class="reasons">${data.reasons.map((r) => `<li>${escapeHtml(r)}</li>`).join("")}</ul>` : ""}
        ${cls !== "safe" ? `<div class="warn">⚠ Do not click links or share OTPs from this sender.</div>
          <button class="btn-report" id="report-btn">🚫 BLOCK &amp; REPORT</button>
          <div class="report-msg" id="report-msg"></div>` : ""}
      `;
      box.classList.add(cls);

      const reportBtn = $("report-btn");
      if (reportBtn) {
        reportBtn.onclick = async () => {
          reportBtn.disabled = true;
          reportBtn.textContent = "REPORTING…";
          try {
            const r = await fetch("/api/report", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ email }),
            });
            const d = await r.json();
            $("report-msg").textContent = d.message || d.error || "done";
          } catch (e) {
            $("report-msg").textContent = "report failed: " + e.message;
            reportBtn.disabled = false;
          }
        };
      }
    } catch (err) {
      box.innerHTML = `<div class="badge" style="color:var(--red)">❌ ${escapeHtml(err.message)}</div>`;
      box.classList.add("phishing");
    } finally {
      btn.disabled = false;
      btn.textContent = "SCAN →";
    }
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  $("scan-btn").addEventListener("click", () => {
    const v = $("scan-input").value.trim();
    if (!v || !v.includes("@")) {
      $("scan-result").classList.remove("hidden");
      $("scan-result").innerHTML =
        '<div class="badge" style="color:var(--red)">❌ Enter a valid email address</div>';
      return;
    }
    scan(v);
  });
  $("scan-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") $("scan-btn").click();
  });
  document.querySelectorAll(".chip").forEach((chip) =>
    chip.addEventListener("click", () => {
      $("scan-input").value = chip.dataset.email;
      scan(chip.dataset.email);
    })
  );

  // ── Threat database table ───────────────────────────────────────
  let ALL_THREATS = [];

  async function loadThreats() {
    const body = $("db-body");
    try {
      const res = await fetch("/api/threats");
      const data = await res.json();
      ALL_THREATS = (data.threats || []).sort((a, b) => b.reports - a.reports);
      renderTable();
    } catch (e) {
      body.innerHTML = `<tr><td colspan="5" class="loading">failed to load: ${escapeHtml(e.message)}</td></tr>`;
    }
  }

  function renderTable() {
    const q = ($("db-search").value || "").toLowerCase();
    const f = $("db-filter").value;
    const body = $("db-body");
    const rows = ALL_THREATS.filter(
      (t) =>
        (f === "ALL" || t.status === f) &&
        (!q || t.email.toLowerCase().includes(q) || (t.category || "").toLowerCase().includes(q))
    );
    if (!rows.length) {
      body.innerHTML = '<tr><td colspan="5" class="loading">no matching entries</td></tr>';
      return;
    }
    body.innerHTML = rows
      .map(
        (t) => `<tr>
          <td>${escapeHtml(t.email)}</td>
          <td class="status st-${t.status.toLowerCase()}">${t.status}</td>
          <td>${t.reports}</td>
          <td>${escapeHtml(t.category || "—")}</td>
          <td>${escapeHtml(t.first_seen || "—")}</td>
        </tr>`
      )
      .join("");
    const note = document.querySelector(".count-note");
    if (note) note.textContent = `${rows.length} of ${ALL_THREATS.length} entries`;
  }

  $("db-search").addEventListener("input", renderTable);
  $("db-filter").addEventListener("change", renderTable);

  // ── Stats ───────────────────────────────────────────────────────
  async function loadStats() {
    try {
      const res = await fetch("/api/stats");
      const s = await res.json();
      $("hs-entries").textContent = s.entries;
      $("hs-reports").textContent = s.total_reports;
      $("hs-confirmed").textContent = s.confirmed;

      $("stats-grid").innerHTML = `
        <div class="stat-card" style="border-top-color:var(--cyan)"><b>${s.entries}</b><span>threats in DB</span></div>
        <div class="stat-card" style="border-top-color:var(--yellow)"><b>${s.total_reports}</b><span>community reports</span></div>
        <div class="stat-card" style="border-top-color:var(--red)"><b>${s.confirmed}</b><span>confirmed phishing</span></div>
        <div class="stat-card" style="border-top-color:var(--orange)"><b>${s.suspicious}</b><span>suspicious</span></div>
      `;

      const cats = Object.entries(s.categories || {}).sort((a, b) => b[1] - a[1]);
      $("cat-grid").innerHTML = cats
        .map(([c, n]) => `<div class="cat-card"><b>${n}</b><span>${escapeHtml(c)}</span></div>`)
        .join("");
    } catch (e) {
      /* hero stats stay as placeholders */
    }
  }

  // shareable links: /?email= victim@scam.xyz auto-scans on load
  const shared = new URLSearchParams(location.search).get("email");
  if (shared) {
    $("scan-input").value = shared;
    scan(shared);
  }

  loadThreats();
  loadStats();
})();
