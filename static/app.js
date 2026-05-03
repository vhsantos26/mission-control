// Tab switching
document.querySelectorAll("nav button").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("nav button").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
  });
});

const fmt = (n) => (n == null ? "—" : Number(n).toLocaleString("pt-BR"));
const fmtCost = (n) => (n == null ? "—" : "$" + Number(n).toFixed(2));
const fmtDate = (s) => (s ? s.replace("T", " ").slice(0, 16) : "—");

async function loadOverview() {
  const r = await fetch("/api/overview");
  const d = await r.json();
  document.getElementById("ov-sessions").textContent = fmt(d.total_sessions);
  document.getElementById("ov-input").textContent = fmt(d.total_input_tokens);
  document.getElementById("ov-output").textContent = fmt(d.total_output_tokens);
  document.getElementById("ov-cache").textContent = fmt(d.total_cache_tokens);
  document.getElementById("ov-cost").textContent = fmtCost(d.total_cost);
}

async function loadFeatures() {
  const r = await fetch("/api/features");
  const features = await r.json();
  const tbody = document.getElementById("features-body");
  tbody.innerHTML = "";
  for (const f of features) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${f.project}</td>
      <td>${f.name}</td>
      <td>${fmtDate(f.first_seen)}</td>
      <td>${fmtDate(f.last_seen)}</td>
      <td>${fmt(f.total_tokens)}</td>
      <td>${fmtCost(f.total_cost)}</td>
      <td>${f.pr_url ? `<a href="${f.pr_url}" target="_blank">${f.pr_status || "open"}</a>` : "—"}</td>
    `;
    tbody.appendChild(tr);
  }
}

async function loadSessions() {
  const r = await fetch("/api/sessions?limit=200");
  const sessions = await r.json();
  const tbody = document.getElementById("sessions-body");
  tbody.innerHTML = "";
  for (const s of sessions) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${s.session_id.slice(0, 8)}…</td>
      <td>${s.project}</td>
      <td>${s.feature || "—"}</td>
      <td>${s.branch || "—"}</td>
      <td>${s.model || "—"}</td>
      <td>${fmtDate(s.started_at)}</td>
      <td>${fmt(s.input_tokens + s.output_tokens + s.cache_tokens)}</td>
      <td>${fmtCost(s.cost_usd)}</td>
    `;
    tbody.appendChild(tr);
  }
}

async function refresh() {
  await Promise.all([loadOverview(), loadFeatures(), loadSessions()]);
}

refresh();
setInterval(refresh, 30_000);
