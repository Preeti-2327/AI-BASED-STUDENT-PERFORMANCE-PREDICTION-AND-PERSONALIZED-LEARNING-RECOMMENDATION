/* ============================================================
   SPS · api.js — HTTP layer. Loaded SECOND (after config.js).
   Sections: 1 error type · 2 core request · 3 ML backend API
   4 auth API · 5 resource factory (future /api/* CRUD)
   ============================================================ */

// ---------- 1. Error type ----------
class ApiError extends Error {
  constructor(message, status = 0) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

// ---------- 2. Core request (token-aware, 15s timeout, for /api/*) ----------
async function api(path, method = "GET", body = null, timeoutMs = 15000) {
  const token = localStorage.getItem("token");
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  let res;
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      signal: ctrl.signal,
      headers: { "Content-Type": "application/json", ...(token && { Authorization: `Bearer ${token}` }) },
      body: body ? JSON.stringify(body) : null,
    });
  } catch (err) {
    throw new ApiError(err && err.name === "AbortError" ? "Request timed out. Please try again." : "Cannot reach server. Is the backend running?", 0);
  } finally {
    clearTimeout(timer);
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError(data.error || data.message || "Request failed", res.status);
  return data;
}

// ---------- 3. ML backend API (live Flask routes, no /api prefix) ----------
async function predictGrade(payload) {
  const res = await fetch(ENDPOINTS.predict, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError(data.error || "Prediction failed", res.status);
  return data; // { predicted_grade, performance_level, recommendations, message }
}

async function getHistory() {
  const res = await fetch(ENDPOINTS.history);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError("Unable to load history", res.status);
  return data.history || [];
}

async function deleteHistoryRecord(id) {
  const res = await fetch(ENDPOINTS.deleteRecord(id), { method: "DELETE" });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError(data.error || "Delete failed", res.status);
  return data;
}

// ---------- 4. Auth API (backend auth; auth.js falls back to demo) ----------
const AuthAPI = {
  login: (email, password) => api("/auth/login", "POST", { email, password }),
  register: (payload) => api("/auth/register", "POST", payload),
};

// ---------- 5. Resource factory (future /api/students|teachers|subjects) ----------
function resource(basePath) {
  return {
    list: () => api(basePath),
    get: (id) => api(`${basePath}/${id}`),
    create: (data) => api(basePath, "POST", data),
    update: (id, data) => api(`${basePath}/${id}`, "PUT", data),
    remove: (id) => api(`${basePath}/${id}`, "DELETE"),
  };
}
const StudentsAPI = resource("/students");
const TeachersAPI = resource("/teachers");
const SubjectsAPI = resource("/subjects");
