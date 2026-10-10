/* ============================================================
   SPS · config.js — environment + shared constants.
   Loaded FIRST on every page (before api.js).
   Sections: 1 environment · 2 endpoints · 3 constants
   ============================================================ */

// ---------- 1. Environment ----------
// Local file preview ("") and dev servers → Flask on :5000.
// Deployed pages → same host, port 5000.
const BACKEND_URL = (() => {
  const host = window.location.hostname;
  // Local file preview / dev → Flask on :5000. Deployed behind the same
  // host (frontend + backend together) → same origin, no hardcoded port.
  if (!host || host === "localhost" || host === "127.0.0.1") return "http://127.0.0.1:5000";
  return window.location.origin;
})();
// Reserved base for future /api/* CRUD routes (not live yet).
const API_URL = `${BACKEND_URL}/api`;

// ---------- 2. Endpoints (live Flask routes) ----------
const ENDPOINTS = {
  home: `${BACKEND_URL}/`,
  predict: `${BACKEND_URL}/predict`,
  history: `${BACKEND_URL}/history`,
  deleteRecord: (id) => `${BACKEND_URL}/history/${id}`,
};

// ---------- 3. Shared constants ----------
const ROLES = ["admin", "teacher", "student"];
const LEVELS = ["Needs Improvement", "Average", "Good", "Excellent"];
const DASHBOARD_BY_ROLE = {
  admin: "admin/dashboard.html",
  teacher: "teacher/dashboard.html",
  student: "student/dashboard.html",
};
