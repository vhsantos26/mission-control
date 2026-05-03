// ---------- formatters ----------
const fmt = (n) => (n == null ? "—" : Number(n).toLocaleString("pt-BR"));
const fmtCost = (n) =>
  n == null ? "—" : "$" + Number(n).toFixed(Number(n) < 1 ? 4 : 2);
const fmtDate = (s) => (s ? s.replace("T", " ").slice(0, 16) : "—");
const fmtDay = (s) => (s ? s.slice(0, 10) : "—");

// ---------- filter state ----------
const filters = {
  project: "",
  rangeDays: 30,
};

function sinceUntil() {
  if (filters.rangeDays === 0) return { since: null, until: null };
  const until = new Date();
  const since = new Date(until);
  since.setDate(until.getDate() - filters.rangeDays);
  return {
    since: since.toISOString(),
    until: until.toISOString(),
  };
}

function qs(extra = {}) {
  const { since, until } = sinceUntil();
  const params = new URLSearchParams();
  if (filters.project) params.set("project", filters.project);
  if (since) params.set("since", since);
  if (until) params.set("until", until);
  for (const [k, v] of Object.entries(extra)) {
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
    // Resize charts when their tab becomes visible
    if (btn.dataset.tab === "overview") {
      setTimeout(() => {
        dailyChart && dailyChart.resize();
        projectsChart && projectsChart.resize();
      }, 50);
    }
  });
});

// ---------- filter wiring ----------
document.getElementById("filter-project").addEventListener("change", (e) => {
  filters.project = e.target.value;
  refresh();
});
document.getElementById("filter-range").addEventListener("change", (e) => {
  filters.rangeDays = Number(e.target.value);
  refresh();
});

document.getElementById("features-search").addEventListener("input", (e) => {
  const q = e.target.value.trim().toLowerCase();
  document.querySelectorAll("#features-body tr").forEach((tr) => {
    const text = tr.textContent.toLowerCase();
    tr.style.display = text.includes(q) ? "" : "none";
  });
});

// ---------- chart instances ----------
let dailyChart, projectsChart;

function ensureCharts() {
  if (!dailyChart) {
    dailyChart = echarts.init(document.getElementById("chart-daily"), "dark", {
      renderer: "canvas",
    });
  }
  if (!projectsChart) {
    projectsChart = echarts.init(
      document.getElementById("chart-projects"),
      "dark",
      { renderer: "canvas" }
    );
  }
}

window.addEventListener("resize", () => {
  dailyChart && dailyChart.resize();
  projectsChart && projectsChart.resize();
});

// ---------- data loaders ----------
async function loadProjectFilter() {
  const r = await fetch("/api/projects");
  const projects = await r.json();
  const sel = document.getElementById("filter-project");
  // Preserve current selection
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
  document.getElementById("ov-input").textContent = fmt(d.total_input_tokens);
  document.getElementById("ov-output").textContent = fmt(d.total_output_tokens);
  document.getElementById("ov-cache").textContent = fmt(d.total_cache_tokens);
  document.getElementById("ov-cost").textContent = fmtCost(d.total_cost);
}

async function loadDailyChart() {
  ensureCharts();
  const days = filters.rangeDays || 30;
  const r = await fetch("/api/daily-cost?days=" + days + "&" + qs().slice(1));
  const data = await r.json();
  dailyChart.setOption({
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
    tooltip: {
      trigger: "axis",
      formatter: (params) => {
        const p = params[0];
        return `${p.axisValue}<br/>${fmtCost(p.value)} (${fmt(p.data.tokens || 0)} tokens, ${fmt(p.data.sessions || 0)} sessions)`;
      },
    },
    xAxis: { type: "category", data: data.map((d) => d.day) },
    yAxis: {
      type: "value",
      axisLabel: { formatter: (v) => "$" + v.toFixed(0) },
    },
    series: [
      {
        type: "bar",
        data: data.map((d) => ({
          value: d.cost,
          tokens: d.tokens,
          sessions: d.sessions,
        })),
        itemStyle: { color: "#4a7cff" },
      },
    ],
  });
}

async function loadProjectsChart() {
  ensureCharts();
  const r = await fetch("/api/sessions?limit=10000" + (qs() && "&" + qs().slice(1)));
  const sessions = await r.json();
  // Aggregate cost by project (respects current filters since /api/sessions does)
  const byProject = {};
  for (const s of sessions) {
    byProject[s.project] = (byProject[s.project] || 0) + (s.cost_usd || 0);
  }
  const data = Object.entries(byProject)
    .filter(([, v]) => v > 0)
    .map(([name, value]) => ({ name, value: Number(value.toFixed(2)) }))
    .sort((a, b) => b.value - a.value);

  projectsChart.setOption({
    tooltip: {
      trigger: "item",
      formatter: (p) => `${p.name}<br/>${fmtCost(p.value)} (${p.percent}%)`,
    },
    legend: { type: "scroll", orient: "vertical", right: 10, top: 20 },
    series: [
      {
        type: "pie",
        radius: ["40%", "70%"],
        center: ["35%", "50%"],
        avoidLabelOverlap: true,
        label: { show: false },
        data,
      },
    ],
  });

  // Also populate Projects tab table
  const totalCost = data.reduce((acc, d) => acc + d.value, 0);
  const tbody = document.getElementById("projects-body");
  tbody.innerHTML = "";
  // Need session counts and tokens — fetch summary
  const counts = {};
  const tokens = {};
  for (const s of sessions) {
    counts[s.project] = (counts[s.project] || 0) + 1;
    tokens[s.project] =
      (tokens[s.project] || 0) +
      (s.input_tokens + s.output_tokens + s.cache_tokens);
  }
  for (const d of data) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${d.name}</td>
      <td>${fmt(counts[d.name])}</td>
      <td>${fmt(tokens[d.name])}</td>
      <td>${fmtCost(d.value)}</td>
      <td>${totalCost ? ((d.value / totalCost) * 100).toFixed(1) : "0"}%</td>
    `;
    tbody.appendChild(tr);
  }
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
      <td>${fmtDay(f.first_seen)}</td>
      <td>${fmtDay(f.last_seen)}</td>
      <td>${fmt(f.total_tokens)}</td>
      <td>${fmtCost(f.total_cost)}</td>
      <td>${f.pr_url ? `<a href="${f.pr_url}" target="_blank">${f.pr_status || "open"}</a>` : "—"}</td>
    `;
    tbody.appendChild(tr);
  }
}

async function loadSessions() {
  const r = await fetch("/api/sessions?limit=200" + (qs() && "&" + qs().slice(1)));
  const sessions = await r.json();
  const tbody = document.getElementById("sessions-body");
  tbody.innerHTML = "";
  for (const s of sessions) {
    const tr = document.createElement("tr");
    tr.className = "expandable";
    tr.dataset.sessionId = s.session_id;
    tr.innerHTML = `
      <td></td>
      <td><code>${s.session_id.slice(0, 8)}</code></td>
      <td>${s.project}</td>
      <td>${s.feature || "—"}</td>
      <td><span class="muted">${s.branch || "—"}</span></td>
      <td>${s.model || "—"}</td>
      <td>${fmtDate(s.started_at)}</td>
      <td>${fmt(s.input_tokens + s.output_tokens + s.cache_tokens)}</td>
      <td>${fmtCost(s.cost_usd)}</td>
    `;
    tr.addEventListener("click", () => toggleSessionDrillDown(tr, s.session_id));
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
    detail.innerHTML = `<td colspan="9" style="padding: 16px;"><span class="muted">Sem prompts registrados pra essa sessão.</span></td>`;
  } else {
    detail.innerHTML = `
      <td colspan="9">
        <table class="prompts-table">
          <thead>
            <tr><th>Quando</th><th>Role</th><th>Input</th><th>Output</th><th>Cache</th><th>Custo</th></tr>
          </thead>
          <tbody>
            ${prompts
              .map(
                (p) => `
              <tr>
                <td>${fmtDate(p.ts)}</td>
                <td><span class="muted">${p.role}</span></td>
                <td>${fmt(p.input_tokens)}</td>
                <td>${fmt(p.output_tokens)}</td>
                <td>${fmt(p.cache_tokens)}</td>
                <td>${fmtCost(p.cost_usd)}</td>
              </tr>
            `
              )
              .join("")}
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
    loadDailyChart(),
    loadProjectsChart(),
    loadFeatures(),
    loadSessions(),
  ]);
}

// Initial load
loadProjectFilter().then(refresh);

// Periodic refresh
setInterval(refresh, 30_000);
