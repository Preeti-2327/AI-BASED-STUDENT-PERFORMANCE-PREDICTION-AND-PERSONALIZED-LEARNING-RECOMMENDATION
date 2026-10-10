/* ============================================================
   SPS · auth.js — login / register / logout + form bindings.
   Loaded on login.html / register.html AFTER api/guard/utils.
   Sections: 1 session · 2 login · 3 register · 4 logout
   5 form UI bindings
   ============================================================ */

// ---------- 1. Session ----------
function saveSession({ token, role, username }) {
  localStorage.setItem("token", token);
  localStorage.setItem("role", role);
  if (username) localStorage.setItem("username", username);
}
function guessRole(email = "") {
  const e = String(email).toLowerCase();
  if (e.startsWith("admin")) return "admin";
  if (e.startsWith("teach") || e.includes("teacher")) return "teacher";
  return "student";
}

// ---------- 2. Login (backend → offline demo fallback) ----------
async function login(email, password, role) {
  try {
    const data = await AuthAPI.login(email, password);
    saveSession({ token: data.token, role: data.role, username: data.username || email.split("@")[0] });
    toast(`Welcome, ${data.role}!`);
    goToDashboard(data.role);
  } catch {
    const demoRole = role || guessRole(email);
    saveSession({ token: "demo-token", role: demoRole, username: (email || demoRole).split("@")[0] });
    toast("Demo mode — backend auth unavailable");
    goToDashboard(demoRole);
  }
}

// ---------- 3. Register (backend → offline demo fallback) ----------
async function register(payload) {
  try {
    const data = await AuthAPI.register(payload);
    saveSession({ token: data.token, role: data.role, username: data.username || payload.name });
    toast("Account created!");
    goToDashboard(data.role);
  } catch {
    const demoRole = payload.role || "student";
    saveSession({ token: "demo-token", role: demoRole, username: payload.name || payload.email.split("@")[0] });
    toast("Demo mode — account saved locally");
    goToDashboard(demoRole);
  }
}

// ---------- 4. Logout ----------
function logout() {
  localStorage.clear();
  window.location.href = (typeof loginUrl === "function" ? loginUrl() : "login.html");
}

// ---------- 5. Form UI bindings ----------
// Role cards: .role-card[data-role] + hidden input #role
function bindRoleCards(containerId = "roleGrid", hiddenId = "role") {
  const box = document.getElementById(containerId);
  if (!box) return;
  box.addEventListener("click", (e) => {
    const card = e.target.closest(".role-card");
    if (!card) return;
    box.querySelectorAll(".role-card").forEach((c) => c.classList.remove("selected"));
    card.classList.add("selected");
    const hidden = document.getElementById(hiddenId);
    if (hidden) hidden.value = card.dataset.role;
  });
}
// Password eye toggles: button[data-pass-toggle] → input#<target>
function bindPasswordToggles() {
  document.querySelectorAll("[data-pass-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const input = document.getElementById(btn.dataset.passToggle);
      if (!input) return;
      input.type = input.type === "password" ? "text" : "password";
      btn.textContent = input.type === "password" ? "👁" : "🙈";
    });
  });
}
function showAuthError(msg) {
  const el = document.getElementById("authError");
  if (el) {
    el.textContent = msg;
    el.classList.add("show");
  } else {
    toast(msg);
  }
}
// Wire-up helpers for future login/register forms
function handleLoginForm(formId = "loginForm") {
  const form = document.getElementById(formId);
  if (!form) return;
  bindRoleCards();
  bindPasswordToggles();
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const email = form.email?.value.trim();
    const password = form.password?.value;
    const role = document.getElementById("role")?.value;
    if (!email || !password) return showAuthError("Email and password are required.");
    login(email, password, role);
  });
}
function handleRegisterForm(formId = "registerForm") {
  const form = document.getElementById(formId);
  if (!form) return;
  bindRoleCards();
  bindPasswordToggles();
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const payload = {
      name: form.name?.value.trim(),
      email: form.email?.value.trim(),
      password: form.password?.value,
      role: document.getElementById("role")?.value || "student",
    };
    if (!payload.name || !payload.email || !payload.password) return showAuthError("All fields are required.");
    register(payload);
  });
}
