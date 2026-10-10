/* ============================================================
   SPS · teacher.js — teacher portal logic (roster, at-risk,
   attendance, marks + prediction).
   Loaded on teacher/*.html AFTER config/api/guard/utils/charts.
   Exposes: Teacher namespace (no globals pollution).
   Sections: 1 store · 2 roster · 3 at-risk · 4 attendance
   5 marks & prediction · 6 demo + shell
   ============================================================ */
const Teacher = (() => {
  // ---------- 1. Store (own keys — admin.js is not loaded here) ----------
  const STUDENTS_KEY = "sps_students";
  const ATT_KEY = "sps_attendance";

  function readStudents() {
    try { return JSON.parse(localStorage.getItem(STUDENTS_KEY)) || []; }
    catch { return []; }
  }

  // ---------- 2. Roster ----------
  function roster() {
    return readStudents();
  }
  function searchRoster(q = "") {
    const needle = q.toLowerCase();
    return readStudents().filter(s => !needle || (s.name + s.id + (s.email || "")).toLowerCase().includes(needle));
  }

  // ---------- 3. At-risk (live history → local fallback) ----------
  async function atRisk() {
    try {
      const history = await getHistory();
      if (history.length) return history.filter(r => r.performance_level === "Needs Improvement");
    } catch { /* offline → local */ }
    return readStudents().filter(s => s.level === "Needs Improvement");
  }

  // ---------- 4. Attendance (local day-wise map: { [date]: { [id]: true } }) ----------
  function today() {
    return new Date().toISOString().slice(0, 10);
  }
  function getAttendance(date = today()) {
    const all = load(ATT_KEY, {});
    return all[date] || {};
  }
  function markAttendance(date, presentMap) {
    const all = load(ATT_KEY, {});
    all[date] = presentMap;
    store(ATT_KEY, all);
    const n = Object.values(presentMap).filter(Boolean).length;
    toast(`Attendance saved — ${n} present ✓`);
    return all[date];
  }
  function attendancePct(studentId) {
    const all = load(ATT_KEY, {});
    const days = Object.keys(all);
    if (!days.length) return null;
    const present = days.filter(d => all[d][studentId]).length;
    return Math.round((present / days.length) * 100);
  }

  // ---------- 5. Marks & prediction (live Flask /predict) ----------
  async function predictFor(payload) {
    return predictGrade(payload);
  }

  // ---------- 6. Demo + shell (sidebar, user chip, logout) ----------
  function seedDemo() {
    if (!localStorage.getItem("token")) {
      localStorage.setItem("token", "demo-token");
      localStorage.setItem("role", "teacher");
      localStorage.setItem("username", "Demo Teacher");
    }
    if (!localStorage.getItem(STUDENTS_KEY)) {
      localStorage.setItem(STUDENTS_KEY, JSON.stringify([
        { id: "STU-001", name: "Aarav Sharma", email: "aarav@example.com", grade: "10-A", level: "Good", attendance: 92, avg: 14.2 },
        { id: "STU-002", name: "Diya Patel", email: "diya@example.com", grade: "10-B", level: "Excellent", attendance: 97, avg: 17.1 },
        { id: "STU-003", name: "Kabir Singh", email: "kabir@example.com", grade: "9-A", level: "Needs Improvement", attendance: 68, avg: 8.4 },
        { id: "STU-004", name: "Ananya Iyer", email: "ananya@example.com", grade: "10-A", level: "Average", attendance: 84, avg: 11.6 },
        { id: "STU-005", name: "Vivaan Rao", email: "vivaan@example.com", grade: "9-B", level: "Good", attendance: 90, avg: 13.8 },
      ]));
    }
  }
  function bindShell() {
    const btn = document.getElementById("menuBtn");
    const side = document.getElementById("sidebar");
    if (btn && side) btn.addEventListener("click", () => side.classList.toggle("open"));
    if (btn) { btn.setAttribute("aria-label", "Toggle navigation menu"); btn.setAttribute("aria-expanded", "false"); btn.addEventListener("click", () => btn.setAttribute("aria-expanded", side.classList.contains("open") ? "true" : "false")); }
    const page = location.pathname.split("/").pop();
    document.querySelectorAll(".nav a[data-page]").forEach(a => {
      if (a.dataset.page === page) a.classList.add("active");
    });
    const name = localStorage.getItem("username") || "Teacher";
    document.querySelectorAll("[data-username]").forEach(el => el.textContent = name);
    document.querySelectorAll("[data-logout]").forEach(el =>
      el.addEventListener("click", e => { e.preventDefault(); localStorage.clear(); location.href = "../login.html"; }));
    const year = document.getElementById("year");
    if (year) year.textContent = new Date().getFullYear();
  }

  return { roster, searchRoster, atRisk, today, getAttendance, markAttendance, attendancePct, predictFor, seedDemo, bindShell };
})();
