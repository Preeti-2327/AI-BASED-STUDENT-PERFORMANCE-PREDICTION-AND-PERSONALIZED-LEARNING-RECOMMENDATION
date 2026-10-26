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
  // If the second-to-last part is admin, student, or teacher, we need to go up one level
  const currentDir = parts.length > 1 ? parts[parts.length - 2] : "";
  if (["admin", "student", "teacher"].includes(currentDir)) return "../";
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
