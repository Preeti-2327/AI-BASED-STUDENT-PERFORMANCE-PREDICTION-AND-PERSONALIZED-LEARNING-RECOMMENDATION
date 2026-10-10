/* ============================================================
   SPS · charts.js — dependency-free canvas charts (no CDN).
   Sections: 1 bar chart · 2 donut chart
   ============================================================ */

// ---------- 1. Bar chart ----------
function drawBarChart(canvas, labels, values, color = "#2c7be5") {
  if (!canvas) return;
  canvas.setAttribute("role", "img");
  canvas.setAttribute("aria-label", "Bar chart: " + labels.map((l, i) => l + " " + values[i]).join(", "));
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.clientWidth || 400, H = 220;
  canvas.width = W * dpr; canvas.height = H * dpr;
  const ctx = canvas.getContext("2d"); ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, W, H);
  const max = Math.max(...values, 1);
  const padL = 8, padB = 26, padT = 12, gap = 10;
  const bw = (W - padL * 2 - gap * (values.length - 1)) / values.length;
  values.forEach((v, i) => {
    const h = ((H - padB - padT) * v) / max;
    const x = padL + i * (bw + gap), y = H - padB - h;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.roundRect ? ctx.roundRect(x, y, bw, h, 5) : ctx.rect(x, y, bw, h);
    ctx.fill();
    ctx.fillStyle = "#1f3a5f"; ctx.font = "bold 11px Segoe UI, Arial"; ctx.textAlign = "center";
    ctx.fillText(String(v), x + bw / 2, y - 4);
    ctx.fillStyle = "#6b7a90"; ctx.font = "11px Segoe UI, Arial";
    ctx.fillText(String(labels[i]).slice(0, 10), x + bw / 2, H - 8);
  });
}

// ---------- 2. Donut chart ----------
// segments: [{ label, value, color }]
function drawDonut(canvas, segments) {
  if (!canvas) return;
  canvas.setAttribute("role", "img");
  canvas.setAttribute("aria-label", "Donut chart: " + segments.map(s => s.label + " " + s.value).join(", "));
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.clientWidth || 300, H = 220;
  canvas.width = W * dpr; canvas.height = H * dpr;
  const ctx = canvas.getContext("2d"); ctx.scale(dpr, dpr);
  const total = segments.reduce((s, x) => s + x.value, 0) || 1;
  const cx = W / 2, cy = H / 2 - 8, R = 70, r = 44;
  let a = -Math.PI / 2;
  segments.forEach(s => {
    const a2 = a + (s.value / total) * Math.PI * 2;
    ctx.beginPath();
    ctx.arc(cx, cy, R, a, a2); ctx.arc(cx, cy, r, a2, a, true);
    ctx.closePath(); ctx.fillStyle = s.color; ctx.fill();
    a = a2;
  });
  ctx.fillStyle = "#1f3a5f"; ctx.font = "bold 18px Segoe UI, Arial"; ctx.textAlign = "center";
  ctx.fillText(String(total), cx, cy + 6);
  // legend (first row)
  ctx.font = "11px Segoe UI, Arial"; ctx.textAlign = "left";
  let ly = H - 22;
  const perRow = Math.ceil(segments.length / 2);
  segments.slice(0, perRow).forEach((s, i) => {
    const x = 10 + i * ((W - 20) / perRow);
    ctx.fillStyle = s.color; ctx.fillRect(x, ly - 8, 10, 10);
    ctx.fillStyle = "#444"; ctx.fillText(`${s.label} (${s.value})`, x + 14, ly);
  });
}
