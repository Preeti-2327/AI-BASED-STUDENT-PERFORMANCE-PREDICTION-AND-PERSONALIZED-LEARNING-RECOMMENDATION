/* ============================================================
   SPS · utils.js — shared helpers (no dependencies).
   Sections: 1 feedback · 2 formatting · 3 storage
   4 export · 5 security
   ============================================================ */

// ---------- 1. Feedback ----------
function toast(msg) {
  let el = document.querySelector(".toast");
  if (!el) { el = document.createElement("div"); el.className = "toast"; document.body.appendChild(el); }
  el.textContent = msg;
  el.classList.add("show");
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove("show"), 2600);
}

// ---------- 2. Formatting ----------
function initials(name) {
  return String(name || "?").trim().split(/\s+/).slice(0, 2).map(s => s[0]).join("").toUpperCase();
}
function fmtDate(iso) {
  try { return new Date(iso).toLocaleString(); } catch { return iso || "-"; }
}
function levelBadge(levelOrGrade) {
  let level = String(levelOrGrade || "");
  const g = parseFloat(levelOrGrade);
  if (!isNaN(g)) level = g < 10 ? "Needs Improvement" : g < 13 ? "Average" : g < 16 ? "Good" : "Excellent";
  const cls = level === "Excellent" ? "ok" : level === "Good" ? "info" : level === "Average" ? "warn" : "danger";
  return `<span class="badge ${cls}">${escapeHtml(level)}</span>`;
}

// ---------- 3. Storage (JSON-safe localStorage) ----------
function store(key, val) { localStorage.setItem(key, JSON.stringify(val)); }
function load(key, fallback) {
  try { const v = JSON.parse(localStorage.getItem(key)); return v ?? fallback; }
  catch { return fallback; }
}

// ---------- 4. Export ----------
function downloadCSV(filename, rows) {
  if (!rows.length) return toast("Nothing to export");
  const head = Object.keys(rows[0]);
  const esc = v => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const csv = [head.join(","), ...rows.map(r => head.map(h => esc(r[h])).join(","))].join("\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

// ---------- 5. Security ----------
function escapeHtml(str) {
  return String(str ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
