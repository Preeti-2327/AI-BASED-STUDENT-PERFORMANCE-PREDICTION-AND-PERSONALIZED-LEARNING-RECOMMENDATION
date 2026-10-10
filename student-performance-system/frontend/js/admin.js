/* ============================================================
   SPS · admin.js — shared admin logic (directory seed data,
   sidebar shell, live backend wiring).
   Loaded on admin/*.html AFTER config/api/guard/utils/charts.
   Sections: 1 constants · 2 demo seed · 3 backend
   4 shell (sidebar/user) · 5 init
   ============================================================ */

// ---------- 1. Constants ----------
// Resolved in config.js (same-origin in production, :5000 in dev).
const BACKEND = (typeof BACKEND_URL !== "undefined") ? BACKEND_URL : "http://127.0.0.1:5000";
const LS = { students: "sps_students", teachers: "sps_teachers", subjects: "sps_subjects" };

// ---------- 2. Demo seed (offline-first directory data) ----------
function seedIfEmpty() {
  // Demo login so static preview works without auth backend
  if (!localStorage.getItem("role")) {
    localStorage.setItem("role", "admin");
    localStorage.setItem("token", "demo-token");
    localStorage.setItem("username", "Admin");
  }
  if (!localStorage.getItem(LS.students)) store(LS.students, [
    { id: "STU-001", name: "Aarav Sharma", email: "aarav@example.com", grade: "10-A", level: "Good", attendance: 92, avg: 14.2 },
    { id: "STU-002", name: "Diya Patel", email: "diya@example.com", grade: "10-B", level: "Excellent", attendance: 97, avg: 17.1 },
    { id: "STU-003", name: "Kabir Singh", email: "kabir@example.com", grade: "9-A", level: "Needs Improvement", attendance: 68, avg: 8.4 },
    { id: "STU-004", name: "Ananya Iyer", email: "ananya@example.com", grade: "10-A", level: "Average", attendance: 84, avg: 11.6 },
    { id: "STU-005", name: "Vivaan Rao", email: "vivaan@example.com", grade: "9-B", level: "Good", attendance: 90, avg: 13.8 },
  ]);
  if (!localStorage.getItem(LS.teachers)) store(LS.teachers, [
    { id: "TCH-01", name: "Meera Nair", email: "meera@school.edu", subject: "Mathematics", classes: 4, status: "Active" },
    { id: "TCH-02", name: "Rahul Verma", email: "rahul@school.edu", subject: "Science", classes: 3, status: "Active" },
    { id: "TCH-03", name: "Sara Khan", email: "sara@school.edu", subject: "English", classes: 5, status: "On Leave" },
  ]);
  if (!localStorage.getItem(LS.subjects)) store(LS.subjects, [
    { code: "MATH-10", name: "Mathematics", teacher: "Meera Nair", credits: 4, students: 58, color: "#2c7be5", progress: 72 },
    { code: "SCI-10", name: "Science", teacher: "Rahul Verma", classes: 3, credits: 4, students: 55, color: "#28a745", progress: 64 },
    { code: "ENG-10", name: "English", teacher: "Sara Khan", credits: 3, students: 60, color: "#f0ad4e", progress: 81 },
    { code: "SST-09", name: "Social Science", teacher: "Rahul Verma", credits: 3, students: 47, color: "#6f42c1", progress: 58 },
  ]);
}

// ---------- 3. Backend (real predictions; [] when offline) ----------
async function fetchHistory() {
  try {
    const res = await fetch(`${BACKEND}/history`);
    if (!res.ok) throw new Error();
    const data = await res.json();
    return data.history || [];
  } catch { return []; }
}

// ---------- 4. Shell (active nav, drawer, user chip, logout) ----------
function setActiveNav() {
  const page = location.pathname.split("/").pop();
  document.querySelectorAll(".nav a[data-page]").forEach(a => {
    if (a.dataset.page === page) a.classList.add("active");
  });
}
function bindShell() {
  const btn = document.getElementById("menuBtn");
  const side = document.getElementById("sidebar");
  if (btn && side) btn.addEventListener("click", () => side.classList.toggle("open"));
  if (btn) { btn.setAttribute("aria-label", "Toggle navigation menu"); btn.setAttribute("aria-expanded", "false"); btn.addEventListener("click", () => btn.setAttribute("aria-expanded", side.classList.contains("open") ? "true" : "false")); }
  const name = localStorage.getItem("username") || "Admin";
  document.querySelectorAll("[data-username]").forEach(el => el.textContent = name);
  document.querySelectorAll("[data-logout]").forEach(el =>
    el.addEventListener("click", e => { e.preventDefault(); localStorage.clear(); location.href = "../login.html"; }));
  const year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();
}

// ---------- 5. Init ----------
document.addEventListener("DOMContentLoaded", () => { seedIfEmpty(); bindShell(); setActiveNav(); });
