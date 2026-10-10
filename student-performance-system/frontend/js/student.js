/* ============================================================
   SPS · student.js — student portal logic (profile, my grades,
   predictions, recommendations, study habits).
   Loaded on student/*.html AFTER config/api/guard/utils/charts.
   Exposes: Student namespace (no globals pollution).
   Sections: 1 store · 2 profile · 3 grades · 4 prediction
   5 recommendations · 6 study habits · 7 demo + shell
   ============================================================ */
const Student = (() => {
  // ---------- 1. Store ----------
  const PROFILE_KEY = "sps_student_profile";
  const HABITS_KEY = "sps_study_habits";

  // ---------- 2. Profile ----------
  function getProfile() {
    return load(PROFILE_KEY, { name: "Demo Student", email: "student@example.com", grade: "10-A" });
  }
  function saveProfile(patch) {
    const next = { ...getProfile(), ...patch };
    store(PROFILE_KEY, next);
    toast("Profile saved ✓");
    return next;
  }

  // ---------- 3. Grades (live history → email match → demo) ----------
  async function myGrades() {
    const me = getProfile();
    try {
      const all = await getHistory();
      if (!all.length) return demoGrades();
      const mine = all.filter(h => (h.student_data?.email || "").toLowerCase() === (me.email || "").toLowerCase());
      return (mine.length ? mine : all.slice(0, 5)).map(r => ({
        grade: r.predicted_grade, level: r.performance_level, when: r.created_at, id: r.id,
      }));
    } catch { return demoGrades(); }
  }
  function demoGrades() {
    return load("sps_students", []).slice(0, 5).map(s => ({ grade: s.avg, level: s.level, when: new Date().toISOString(), id: s.id }));
  }

  // ---------- 4. Prediction (live Flask /predict) ----------
  async function runPrediction(payload) {
    return predictGrade(payload);
  }

  // ---------- 5. Recommendations (render helper) ----------
  function renderRecommendations(list) {
    if (!list?.length) return `<p class="empty">No recommendations yet — run a prediction first.</p>`;
    return list.map(r => {
      const text = typeof r === "string" ? r : (r.title || r.topic || JSON.stringify(r));
      return `<div class="card mb-1">🎯 ${escapeHtml(text)}</div>`;
    }).join("");
  }

  // ---------- 6. Study habits (local routine tracker) ----------
  function getHabits() {
    return load(HABITS_KEY, { hoursPerDay: 2, focus: "Mathematics", revisionDays: 3, updatedAt: null });
  }
  function saveHabits(patch) {
    const next = { ...getHabits(), ...patch, updatedAt: new Date().toISOString() };
    store(HABITS_KEY, next);
    toast("Study plan saved ✓");
    return next;
  }

  // ---------- 7. Demo + shell (sidebar, user chip, logout) ----------
  function seedDemo() {
    if (!localStorage.getItem("token")) {
      localStorage.setItem("token", "demo-token");
      localStorage.setItem("role", "student");
      localStorage.setItem("username", getProfile().name);
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
    const name = localStorage.getItem("username") || getProfile().name;
    document.querySelectorAll("[data-username]").forEach(el => el.textContent = name);
    document.querySelectorAll("[data-logout]").forEach(el =>
      el.addEventListener("click", e => { e.preventDefault(); localStorage.clear(); location.href = "../login.html"; }));
    const year = document.getElementById("year");
    if (year) year.textContent = new Date().getFullYear();
  }

  return { getProfile, saveProfile, myGrades, runPrediction, renderRecommendations, getHabits, saveHabits, seedDemo, bindShell };
})();
