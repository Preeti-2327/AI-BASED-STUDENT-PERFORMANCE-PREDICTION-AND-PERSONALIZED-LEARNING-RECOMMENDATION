/* ============================================================
   SPS · guard.js — route protection. After config.js.
   Sections: 1 session · 2 guards · 3 redirects
   ============================================================ */

// ---------- 1. Session ----------
function getSession() {
  return {
    token: localStorage.getItem("token"),
    role: localStorage.getItem("role"),
    username: localStorage.getItem("username"),
  };
}
function isLoggedIn() {
  return !!getSession().token;
}

// ---------- 2. Guards (call at top of protected pages) ----------
function requireAuth() {
  if (!isLoggedIn()) redirectToLogin();
}
function requireRole(allowed) {
  const { token, role } = getSession();
  if (!token || !allowed.includes(role)) redirectToLogin();
}

// ---------- 3. Redirects (sub-path safe: works at / and /repo-name/) ----------
function appRoot() {
  const parts = location.pathname.split("/").filter(Boolean);
  // Portal pages live one level deep (/admin, /student, /teacher).
  if (parts.length && ["admin", "student", "teacher"].includes(parts[0])) return "../";
  return "";
}
function loginUrl() {
  return appRoot() + "login.html";
}
function redirectToLogin() {
  window.location.href = loginUrl();
}
function goToDashboard(role) {
  window.location.href = appRoot() + (DASHBOARD_BY_ROLE[role] || DASHBOARD_BY_ROLE.student);
}
