// ---------- i18n ----------
let lang = localStorage.getItem("mc_lang") || "en";

const LOCALES = {
  en: {
    nav_overview: "Overview",
    nav_features: "Features",
    nav_sessions: "Sessions",
    nav_projects: "Projects",
    nav_settings: "Settings",
    filter_all_projects: "All projects",
    filter_all_models: "All models",
    card_sessions: "Sessions",
    card_turns: "Turns",
    card_input: "Input",
    card_output: "Output",
    card_cache_read: "Cache Read",
    card_cache_create: "Cache Create",
    card_cost: "Cost (USD)",
    explainer_summary: "What do these numbers mean?",
    explainer_expand: "— click to expand",
    explainer_sessions: "<strong>Sessions</strong> — Distinct Claude Code conversations (1 JSONL = 1 session).",
    explainer_turns: "<strong>Turns</strong> — Number of prompts (user → assistant pairs) in the period.",
    explainer_input: "<strong>Input</strong> — Tokens sent to the model. Pricing baseline.",
    explainer_output: "<strong>Output</strong> — Generated tokens. Generally 5× more expensive than input.",
    explainer_cache_read: "<strong>Cache Read</strong> — Tokens reused from cache (CLAUDE.md, long context). ~10× cheaper than input — high numbers here are a <em>good sign</em>.",
    explainer_cache_create: "<strong>Cache Create</strong> — First write to cache. Costs ~1.25× input. When they grow a lot, they indicate large initial prompts.",
    explainer_cost: "<strong>Cost</strong> — API pricing estimate. If you use a flat plan (Pro/Max), the real cost is your subscription — change <code>pricing_plan</code> in <code>~/.mission-control/config.json</code>.",
    chart_daily_work: "Daily work — Input + Output + Cache Create",
    chart_daily_cache: "Daily cache reads",
    chart_daily_cache_sub: "(separate — orders of magnitude larger)",
    chart_by_project: "Tokens by project — Input vs Output",
    chart_by_model: "Token usage by model",
    chart_top_tools: "Top tools",
    chart_top_tools_sub: "— invocations per tool (all filtered sessions)",
    chart_recent: "Recent sessions",
    chart_recent_sub: "— last 8",
    series_input: "input",
    series_output: "output",
    series_cache_create: "cache create",
    series_cache_read: "cache read",
    series_invocations: "invocations",
    chart_tool_empty: "No tool_use data yet — re-run `cli.py scan` after upgrading to v0.5",
    chart_tool_uses_in: "uses in",
    chart_tool_sessions_word: "sessions",
    badge_active: "Active",
    recent_start: "Start",
    recent_project: "Project",
    recent_feature: "Feature",
    recent_model: "Model",
    recent_tokens: "Tokens",
    recent_cost: "Cost",
    feat_search_placeholder: "Filter by feature name…",
    feat_project: "Project",
    feat_feature: "Feature",
    feat_first: "First",
    feat_last: "Last",
    feat_tokens: "Tokens",
    feat_cost: "Cost",
    feat_pr: "PR",
    sess_session: "Session",
    sess_project: "Project",
    sess_feature: "Feature",
    sess_branch: "Branch",
    sess_model: "Model",
    sess_start: "Start",
    sess_tokens: "Tokens",
    sess_cost: "Cost",
    prompts_empty: "No prompts recorded.",
    prompts_when: "When",
    prompts_role: "Role",
    prompts_input: "Input",
    prompts_output: "Output",
    prompts_cache_r: "Cache R",
    prompts_cache_c: "Cache C",
    prompts_cost: "Cost",
    proj_project: "Project",
    proj_sessions: "Sessions",
    proj_tokens: "Tokens",
    proj_cost: "Cost",
    proj_pct: "% of total",
    settings_title: "Settings",
    settings_config_hint: "Pricing plan and thresholds come from <code>~/.mission-control/config.json</code>.",
    settings_active_hint: "Sessions edited in the last 5 minutes are marked as",
    settings_edit_hint: "Edit manually; restart the dashboard to apply.",
    settings_lang_label: "Language",
  },
  pt: {
    nav_overview: "Visão Geral",
    nav_features: "Features",
    nav_sessions: "Sessões",
    nav_projects: "Projetos",
    nav_settings: "Configurações",
    filter_all_projects: "Todos os projetos",
    filter_all_models: "Todos os modelos",
    card_sessions: "Sessões",
    card_turns: "Turns",
    card_input: "Input",
    card_output: "Output",
    card_cache_read: "Cache Read",
    card_cache_create: "Cache Create",
    card_cost: "Custo (USD)",
    explainer_summary: "O que esses números significam?",
    explainer_expand: "— clique para expandir",
    explainer_sessions: "<strong>Sessões</strong> — Conversas Claude Code distintas (1 JSONL = 1 sessão).",
    explainer_turns: "<strong>Turns</strong> — Quantidade de prompts (user → assistant pairs) no período.",
    explainer_input: "<strong>Input</strong> — Tokens enviados ao modelo. Pricing baseline.",
    explainer_output: "<strong>Output</strong> — Tokens gerados. Geralmente 5× mais caros que input.",
    explainer_cache_read: "<strong>Cache Read</strong> — Tokens reutilizados de cache (CLAUDE.md, contexto longo). ~10× mais baratos que input — números altos aqui são <em>bom sinal</em>.",
    explainer_cache_create: "<strong>Cache Create</strong> — Primeira escrita ao cache. Custa ~1.25× input. Quando crescem muito, indicam prompts iniciais grandes.",
    explainer_cost: "<strong>Custo</strong> — Estimativa em pricing API. Se você usa plano flat (Pro/Max), o custo real é o da assinatura — mude <code>pricing_plan</code> em <code>~/.mission-control/config.json</code>.",
    chart_daily_work: "Trabalho diário — Input + Output + Cache Create",
    chart_daily_cache: "Cache reads diários",
    chart_daily_cache_sub: "(separado — ordens de grandeza maior)",
    chart_by_project: "Tokens por projeto — Input vs Output",
    chart_by_model: "Uso de tokens por modelo",
    chart_top_tools: "Top tools",
    chart_top_tools_sub: "— invocações por ferramenta (todas as sessões filtradas)",
    chart_recent: "Sessões recentes",
    chart_recent_sub: "— últimas 8",
    series_input: "input",
    series_output: "output",
    series_cache_create: "cache create",
    series_cache_read: "cache read",
    series_invocations: "invocações",
    chart_tool_empty: "Sem dados de tool_use ainda — re-rodar `cli.py scan` após upgrade pra v0.5",
    chart_tool_uses_in: "usos em",
    chart_tool_sessions_word: "sessões",
    badge_active: "Ativa",
    recent_start: "Início",
    recent_project: "Projeto",
    recent_feature: "Feature",
    recent_model: "Modelo",
    recent_tokens: "Tokens",
    recent_cost: "Custo",
    feat_search_placeholder: "Filtrar por nome de feature…",
    feat_project: "Projeto",
    feat_feature: "Feature",
    feat_first: "Primeira",
    feat_last: "Última",
    feat_tokens: "Tokens",
    feat_cost: "Custo",
    feat_pr: "PR",
    sess_session: "Sessão",
    sess_project: "Projeto",
    sess_feature: "Feature",
    sess_branch: "Branch",
    sess_model: "Modelo",
    sess_start: "Início",
    sess_tokens: "Tokens",
    sess_cost: "Custo",
    prompts_empty: "Sem prompts registrados.",
    prompts_when: "Quando",
    prompts_role: "Role",
    prompts_input: "Input",
    prompts_output: "Output",
    prompts_cache_r: "Cache R",
    prompts_cache_c: "Cache C",
    prompts_cost: "Custo",
    proj_project: "Projeto",
    proj_sessions: "Sessões",
    proj_tokens: "Tokens",
    proj_cost: "Custo",
    proj_pct: "% do total",
    settings_title: "Configurações",
    settings_config_hint: "Pricing plan e thresholds vêm de <code>~/.mission-control/config.json</code>.",
    settings_active_hint: "Sessões com edição nos últimos 5 minutos são marcadas como",
    settings_edit_hint: "Editar manualmente; reiniciar o dashboard pra aplicar.",
    settings_lang_label: "Idioma",
  },
};

function t(key) {
  return LOCALES[lang][key] ?? key;
}

function applyLang() {
  document.documentElement.lang = lang === "pt" ? "pt-BR" : "en";
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-html]").forEach((el) => {
    el.innerHTML = t(el.dataset.i18nHtml);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
}

// ---------- formatters ----------
function fmt(n) {
  if (n == null) return "—";
  return Number(n).toLocaleString(lang === "pt" ? "pt-BR" : "en-US");
}
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

document.getElementById("lang-select").addEventListener("change", (e) => {
  lang = e.target.value;
  localStorage.setItem("mc_lang", lang);
  applyLang();
  loadProjectFilter();
  loadModelFilter();
  refresh();
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
  sel.innerHTML = `<option value="">${t("filter_all_projects")}</option>`;
  for (const p of projects) {
    const opt = document.createElement("option");
    opt.value = p;
    opt.textContent = p;
    sel.appendChild(opt);
  }
  sel.value = current;
}

async function loadModelFilter() {
  const r = await fetch("/api/models");
  const models = await r.json();
  const sel = document.getElementById("filter-model");
  const current = sel.value;
  sel.innerHTML = `<option value="">${t("filter_all_models")}</option>`;
  for (const m of models) {
    const opt = document.createElement("option");
    opt.value = m;
    opt.textContent = m;
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
      { name: t("series_input"), type: "bar", stack: "tokens", data: data.map((d) => d.input_tokens), itemStyle: { color: "#4a7cff" } },
      { name: t("series_output"), type: "bar", stack: "tokens", data: data.map((d) => d.output_tokens), itemStyle: { color: "#a06cff" } },
      { name: t("series_cache_create"), type: "bar", stack: "tokens", data: data.map((d) => d.cache_create_tokens), itemStyle: { color: "#ffaa3a" } },
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
      { name: t("series_cache_read"), type: "bar", data: data.map((d) => d.cache_read_tokens), itemStyle: { color: "#6cbf6c" } },
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
      { name: t("series_input"), type: "bar", data: data.map((d) => d.input_tokens), itemStyle: { color: "#4a7cff" } },
      { name: t("series_output"), type: "bar", data: data.map((d) => d.output_tokens), itemStyle: { color: "#a06cff" } },
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

async function loadByTool() {
  const r = await fetch("/api/by-tool" + qs());
  const data = await r.json();
  if (!data.length) {
    chart("chart-by-tool").setOption({
      title: { text: t("chart_tool_empty"), left: "center", top: "center", textStyle: { color: "#aaa", fontSize: 13 } },
    });
    return;
  }
  // Reverse so largest count appears at the TOP of the horizontal bar (yAxis renders bottom-up)
  const reversed = [...data].reverse();
  chart("chart-by-tool").setOption({
    grid: { left: 130, right: 60, top: 20, bottom: 30 },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter: (p) => `${p[0].name}<br/>${fmt(p[0].value)} ${t("chart_tool_uses_in")} ${reversed[p[0].dataIndex].sessions} ${t("chart_tool_sessions_word")}`,
    },
    yAxis: { type: "category", data: reversed.map((d) => d.tool_name), axisLabel: { color: "#aaa" } },
    xAxis: { type: "value", axisLabel: { color: "#aaa", formatter: (v) => v >= 1e3 ? (v / 1e3).toFixed(1) + "k" : v } },
    series: [
      {
        name: t("series_invocations"),
        type: "bar",
        data: reversed.map((d) => d.total_count),
        itemStyle: { color: "#4ac4a8" },
        label: { show: true, position: "right", color: "#aaa", formatter: (p) => fmt(p.value) },
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
  const activeBadge = s.is_active ? `<span class="badge badge-active">${t("badge_active")}</span>` : "";
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
    const activeBadge = s.is_active ? `<span class="badge badge-active">${t("badge_active")}</span>` : "";
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
      <td>${fmt(d.sessions)}</td>
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
    detail.innerHTML = `<td colspan="9" style="padding: 16px;"><span class="muted">${t("prompts_empty")}</span></td>`;
  } else {
    detail.innerHTML = `
      <td colspan="9">
        <table class="prompts-table">
          <thead>
            <tr><th>${t("prompts_when")}</th><th>${t("prompts_role")}</th><th>${t("prompts_input")}</th><th>${t("prompts_output")}</th><th>${t("prompts_cache_r")}</th><th>${t("prompts_cache_c")}</th><th>${t("prompts_cost")}</th></tr>
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
    loadByTool(),
    loadRecentSessions(),
    loadFeatures(),
    loadSessions(),
    loadProjectsTab(),
  ]);
}

applyLang();
document.getElementById("lang-select").value = lang;
Promise.all([loadProjectFilter(), loadModelFilter()]).then(refresh);
setInterval(refresh, 30_000);
