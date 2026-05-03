// ---------- formatters ----------
const fmt = (n) => (n == null ? "—" : Number(n).toLocaleString("pt-BR"));
const fmtCost = (n) =>
  n == null ? "—" : "$" + Number(n).toFixed(Number(n) < 1 ? 4 : 2);
const fmtDate = (s) => (s ? s.replace("T", " ").slice(0, 16) : "—");

// ---------- filter state ----------
const filters = {
  project: "",
  model: "",
  rangeDays: 30,
};

function sinceUntil() {
  if (filters.rangeDays === 0) return { since: null, until: null };
  const until = new Date();
  const since = new Date(until);
  since.setDate(until.getDate() - filters.rangeDays);
  return { since: since.toISOString(), until: until.toISOString() };
}

function qsObj(extra = {}) {
  const { since, until } = sinceUntil();
  const o = {};
  if (filters.project) o.project = filters.project;
  if (filters.model) o.model = filters.model;
  if (since) o.since = since;
  if (until) o.until = until;
  return { ...o, ...extra };
}

function qs(extra = {}) {
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(qsObj(extra))) {
    if (v != null && v !== "") params.set(k, v);
  }
  const s = params.toString();
  return s ? "?" + s : "";
}

// ---------- tab switching ----------
document.querySelectorAll("nav button").forEach((btn) => {
  btn.addEventListener("click", () => {
    document
      .querySelectorAll("nav button")
      .forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
    if (btn.dataset.tab === "overview") {
      setTimeout(resizeAllCharts, 50);
    }
  });
});

// ---------- filter wiring ----------
document.getElementById("filter-project").addEventListener("change", (e) => {
  filters.project = e.target.value;
  refresh();
});
document.getElementById("filter-model").addEventListener("change", (e) => {
  filters.model = e.target.value;
  refresh();
});
document.querySelectorAll("#range-pills button").forEach((btn) => {
  btn.addEventListener("click", () => {
    document
      .querySelectorAll("#range-pills button")
      .forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    filters.rangeDays = Number(btn.dataset.range);
    refresh();
  });
});

document.getElementById("features-search").addEventListener("input", (e) => {
  const q = e.target.value.trim().toLowerCase();
  document.querySelectorAll("#features-body tr").forEach((tr) => {
    tr.style.display = tr.textContent.toLowerCase().includes(q) ? "" : "none";
  });
});

// ---------- chart instances ----------
const charts = {};
function chart(id) {
  if (!charts[id]) {
    charts[id] = echarts.init(document.getElementById(id), "dark", {
      renderer: "canvas",
    });
  }
  return charts[id];
}
function resizeAllCharts() {
  for (const c of Object.values(charts)) c && c.resize();
}
window.addEventListener("resize", resizeAllCharts);

// ---------- data loaders ----------
async function loadProjectFilter() {
  const r = await fetch("/api/projects");
  const projects = await r.json();
  const sel = document.getElementById("filter-project");
  const current = sel.value;
  sel.innerHTML = '<option value="">All projects</option>';
  for (const p of projects) {
    const opt = document.createElement("option");
    opt.value = p;
    opt.textContent = p;
    sel.appendChild(opt);
  }
  sel.value = current;
}

async function loadOverview() {
  const r = await fetch("/api/overview" + qs());
  const d = await r.json();
  document.getElementById("ov-sessions").textContent = fmt(d.total_sessions);
  document.getElementById("ov-turns").textContent = fmt(d.total_turns);
  document.getElementById("ov-input").textContent = fmt(d.total_input_tokens);
  document.getElementById("ov-output").textContent = fmt(d.total_output_tokens);
  document.getElementById("ov-cache-read").textContent = fmt(d.total_cache_read_tokens);
  document.getElementById("ov-cache-create").textContent = fmt(d.total_cache_create_tokens);
  document.getElementById("ov-cost").textContent = fmtCost(d.total_cost);
}

async function loadDailyWork() {
  const days = filters.rangeDays || 30;
  const r = await fetch("/api/daily-cost?days=" + days + (qs() && "&" + qs().slice(1)));
  const data = await r.json();
  chart("chart-daily-work").setOption({
    grid: { left: 60, right: 20, top: 30, bottom: 30 },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { top: 0, textStyle: { color: "#aaa" } },
    xAxis: { type: "category", data: data.map((d) => d.day) },
    yAxis: { type: "value", axisLabel: { formatter: (v) => v >= 1e6 ? (v / 1e6).toFixed(0) + "M" : v >= 1e3 ? (v / 1e3).toFixed(0) + "k" : v } },
    series: [
      { name: "input", type: "bar", stack: "tokens", data: data.map((d) => d.input_tokens), itemStyle: { color: "#4a7cff" } },
      { name: "output", type: "bar", stack: "tokens", data: data.map((d) => d.output_tokens), itemStyle: { color: "#a06cff" } },
      { name: "cache create", type: "bar", stack: "tokens", data: data.map((d) => d.cache_create_tokens), itemStyle: { color: "#ffaa3a" } },
    ],
  });
}

async function loadDailyCache() {
  const days = filters.rangeDays || 30;
  const r = await fetch("/api/daily-cost?days=" + days + (qs() && "&" + qs().slice(1)));
  const data = await r.json();
  chart("chart-daily-cache").setOption({
    grid: { left: 60, right: 20, top: 30, bottom: 30 },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { top: 0, textStyle: { color: "#aaa" } },
    xAxis: { type: "category", data: data.map((d) => d.day) },
    yAxis: { type: "value", axisLabel: { formatter: (v) => v >= 1e6 ? (v / 1e6).toFixed(0) + "M" : v >= 1e3 ? (v / 1e3).toFixed(0) + "k" : v } },
    series: [
      { name: "cache read", type: "bar", data: data.map((d) => d.cache_read_tokens), itemStyle: { color: "#6cbf6c" } },
    ],
  });
}

async function loadByProject() {
  const r = await fetch("/api/by-project" + qs());
  const data = await r.json();
  chart("chart-by-project").setOption({
    grid: { left: 100, right: 20, top: 30, bottom: 30 },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { top: 0, textStyle: { color: "#aaa" } },
    yAxis: { type: "category", data: data.map((d) => d.project), axisLabel: { color: "#aaa" } },
    xAxis: { type: "value", axisLabel: { formatter: (v) => v >= 1e6 ? (v / 1e6).toFixed(0) + "M" : v >= 1e3 ? (v / 1e3).toFixed(0) + "k" : v } },
    series: [
      { name: "input", type: "bar", data: data.map((d) => d.input_tokens), itemStyle: { color: "#4a7cff" } },
      { name: "output", type: "bar", data: data.map((d) => d.output_tokens), itemStyle: { color: "#a06cff" } },
    ],
  });
}

async function loadByModel() {
  const r = await fetch("/api/by-model" + qs());
  const data = await r.json();
  const pieData = data
    .filter((d) => d.cost > 0)
    .map((d) => ({ name: d.model, value: Number(d.cost.toFixed(2)) }));
  chart("chart-by-model").setOption({
    tooltip: {
      trigger: "item",
      formatter: (p) => `${p.name}<br/>${fmtCost(p.value)} (${p.percent}%)`,
    },
    legend: { type: "scroll", orient: "vertical", right: 10, top: 20, textStyle: { color: "#aaa" } },
    series: [
      {
        type: "pie",
        radius: ["40%", "70%"],
        center: ["35%", "50%"],
        avoidLabelOverlap: true,
        label: { show: false },
        data: pieData,
      },
    ],
  });
}

async function loadFeatures() {
  const r = await fetch("/api/features" + qs());
  const features = await r.json();
  const tbody = document.getElementById("features-body");
  tbody.innerHTML = "";
  for (const f of features) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${f.project}</td>
      <td>${f.name}</td>
      <td>${(f.first_seen || "—").slice(0, 10)}</td>
      <td>${(f.last_seen || "—").slice(0, 10)}</td>
      <td>${fmt(f.total_tokens)}</td>
      <td>${fmtCost(f.total_cost)}</td>
      <td>${f.pr_url ? `<a href="${f.pr_url}" target="_blank">${f.pr_status || "open"}</a>` : "—"}</td>
    `;
    tbody.appendChild(tr);
  }
}

function renderSessionRow(s) {
  const tr = document.createElement("tr");
  tr.className = "expandable";
  if (s.is_active) tr.classList.add("is-active");
  tr.dataset.sessionId = s.session_id;
  const activeBadge = s.is_active ? '<span class="badge badge-active">Ativa</span>' : "";
  tr.innerHTML = `
    <td></td>
    <td>${activeBadge}<code>${s.session_id.slice(0, 8)}</code></td>
    <td>${s.project}</td>
    <td>${s.feature || "—"}</td>
    <td><span class="muted">${s.branch || "—"}</span></td>
    <td>${s.model || "—"}</td>
    <td>${fmtDate(s.started_at)}</td>
    <td>${fmt(s.input_tokens + s.output_tokens + s.cache_tokens)}</td>
    <td>${fmtCost(s.cost_usd)}</td>
  `;
  tr.addEventListener("click", () => toggleSessionDrillDown(tr, s.session_id));
  return tr;
}

async function loadSessions() {
  const r = await fetch("/api/sessions?limit=200" + (qs() && "&" + qs().slice(1)));
  const sessions = await r.json();
  const tbody = document.getElementById("sessions-body");
  tbody.innerHTML = "";
  for (const s of sessions) tbody.appendChild(renderSessionRow(s));
}

async function loadRecentSessions() {
  // Recent sessions widget on Overview — always shows last 8 across all projects/models
  const r = await fetch("/api/sessions?limit=8");
  const sessions = await r.json();
  const tbody = document.getElementById("recent-sessions-body");
  tbody.innerHTML = "";
  for (const s of sessions) {
    const activeBadge = s.is_active ? '<span class="badge badge-active">Ativa</span>' : "";
    const tr = document.createElement("tr");
    if (s.is_active) tr.classList.add("is-active");
    tr.innerHTML = `
      <td>${activeBadge}<code>${s.session_id.slice(0, 8)}</code></td>
      <td>${fmtDate(s.started_at)}</td>
      <td>${s.project}</td>
      <td>${s.feature || "—"}</td>
      <td><span class="muted">${s.model || "—"}</span></td>
      <td>${fmt(s.input_tokens + s.output_tokens + s.cache_tokens)}</td>
      <td>${fmtCost(s.cost_usd)}</td>
    `;
    tbody.appendChild(tr);
  }
}

async function loadProjectsTab() {
  const r = await fetch("/api/by-project" + qs());
  const data = await r.json();
  const tbody = document.getElementById("projects-body");
  tbody.innerHTML = "";
  const total = data.reduce((acc, d) => acc + (d.cost || 0), 0);
  for (const d of data) {
    const tokens = d.input_tokens + d.output_tokens + d.cache_read_tokens + d.cache_create_tokens;
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${d.project}</td>
      <td>—</td>
      <td>${fmt(tokens)}</td>
      <td>${fmtCost(d.cost)}</td>
      <td>${total ? ((d.cost / total) * 100).toFixed(1) : "0"}%</td>
    `;
    tbody.appendChild(tr);
  }
}

async function toggleSessionDrillDown(tr, sessionId) {
  if (tr.classList.contains("expanded")) {
    tr.classList.remove("expanded");
    const next = tr.nextElementSibling;
    if (next && next.classList.contains("prompts-row")) next.remove();
    return;
  }
  tr.classList.add("expanded");
  const r = await fetch(`/api/sessions/${sessionId}/prompts`);
  const prompts = await r.json();
  const detail = document.createElement("tr");
  detail.className = "prompts-row";
  if (prompts.length === 0) {
    detail.innerHTML = `<td colspan="9" style="padding: 16px;"><span class="muted">Sem prompts registrados.</span></td>`;
  } else {
    detail.innerHTML = `
      <td colspan="9">
        <table class="prompts-table">
          <thead>
            <tr><th>Quando</th><th>Role</th><th>Input</th><th>Output</th><th>Cache R</th><th>Cache C</th><th>Custo</th></tr>
          </thead>
          <tbody>
            ${prompts.map((p) => `
              <tr>
                <td>${fmtDate(p.ts)}</td>
                <td><span class="muted">${p.role}</span></td>
                <td>${fmt(p.input_tokens)}</td>
                <td>${fmt(p.output_tokens)}</td>
                <td>${fmt(p.cache_read_tokens)}</td>
                <td>${fmt(p.cache_create_tokens)}</td>
                <td>${fmtCost(p.cost_usd)}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </td>
    `;
  }
  tr.parentNode.insertBefore(detail, tr.nextElementSibling);
}

async function refresh() {
  await Promise.all([
    loadOverview(),
    loadDailyWork(),
    loadDailyCache(),
    loadByProject(),
    loadByModel(),
    loadRecentSessions(),
    loadFeatures(),
    loadSessions(),
    loadProjectsTab(),
  ]);
}

loadProjectFilter().then(refresh);
setInterval(refresh, 30_000);
