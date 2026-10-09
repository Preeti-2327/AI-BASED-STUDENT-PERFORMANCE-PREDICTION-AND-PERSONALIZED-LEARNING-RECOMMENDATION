async function login(email, password) {
  const data = await api("/auth/login", "POST", { email, password });
  localStorage.setItem("token", data.token);
  localStorage.setItem("role", data.role);
  window.location.href = `/${data.role}/dashboard.html`;
}
function logout() { localStorage.clear(); window.location.href = "/login.html"; }
