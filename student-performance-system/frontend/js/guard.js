// Protected page par role check
function requireRole(allowed) {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");
  if (!token || !allowed.includes(role)) window.location.href = "/login.html";
}
