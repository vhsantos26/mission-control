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
    filter_clear_projects: "Clear selection",
    filter_one_project: "1 project",
    filter_n_projects: "{n} projects",
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
    chart_daily_cache: "Daily cache — Create vs Read",
    chart_daily_cache_sub: "(dual axis — read is typically 10–100× larger)",
    cache_ratio_label: "Ratio",
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
    filter_clear_projects: "Limpar seleção",
    filter_one_project: "1 projeto",
    filter_n_projects: "{n} projetos",
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
    chart_daily_cache: "Cache diário — Create vs Read",
    chart_daily_cache_sub: "(eixo duplo — read costuma ser 10–100× maior)",
    cache_ratio_label: "Razão",
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
  project: [],
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
  if (filters.project && filters.project.length) o.project = filters.project;
  if (filters.model) o.model = filters.model;
  if (since) o.since = since;
  if (until) o.until = until;
  return { ...o, ...extra };
}

function qs(extra = {}) {
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(qsObj(extra))) {
    if (v == null || v === "") continue;
    if (Array.isArray(v)) {
      for (const item of v) if (item) params.append(k, item);
    } else {
      params.set(k, v);
    }
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
const projectMs = {
  root: document.getElementById("filter-project"),
  toggle: document.querySelector("#filter-project .ms-toggle"),
  label: document.querySelector("#filter-project .ms-label"),
  panel: document.querySelector("#filter-project .ms-panel"),
};

function updateProjectLabel() {
  const n = filters.project.length;
  if (n === 0) projectMs.label.textContent = t("filter_all_projects");
  else if (n === 1) projectMs.label.textContent = filters.project[0];
  else projectMs.label.textContent = t("filter_n_projects").replace("{n}", n);
}

function openProjectPanel() {
  projectMs.panel.hidden = false;
  projectMs.toggle.setAttribute("aria-expanded", "true");
}

function closeProjectPanel() {
  projectMs.panel.hidden = true;
  projectMs.toggle.setAttribute("aria-expanded", "false");
}

projectMs.toggle.addEventListener("click", (e) => {
  e.stopPropagation();
  if (projectMs.panel.hidden) openProjectPanel();
  else closeProjectPanel();
});

document.addEventListener("click", (e) => {
  if (!projectMs.root.contains(e.target)) closeProjectPanel();
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
  updateProjectLabel();
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
  // Skip charts whose container is display:none — resizing them captures 0x0
  // and corrupts the canvas for the next render. offsetParent is null when
  // the element (or any ancestor) is display:none.
  for (const [id, c] of Object.entries(charts)) {
    if (!c) continue;
    const el = document.getElementById(id);
    if (!el || el.offsetParent === null) continue;
    c.resize();
  }
}
window.addEventListener("resize", resizeAllCharts);

// ---------- data loaders ----------
async function loadProjectFilter() {
  const r = await fetch("/api/projects");
  const projects = await r.json();
  // Drop selections that no longer exist (e.g. after a rescan).
  filters.project = filters.project.filter((p) => projects.includes(p));
  projectMs.panel.innerHTML = "";

  const clear = document.createElement("div");
  clear.className = "ms-option ms-clear";
  clear.textContent = t("filter_clear_projects");
  clear.addEventListener("click", (e) => {
    e.stopPropagation();
    filters.project = [];
    for (const cb of projectMs.panel.querySelectorAll("input[type=checkbox]")) {
      cb.checked = false;
    }
    updateProjectLabel();
    refresh();
  });
  projectMs.panel.appendChild(clear);

  for (const p of projects) {
    const opt = document.createElement("label");
    opt.className = "ms-option";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.value = p;
    cb.checked = filters.project.includes(p);
    cb.addEventListener("change", () => {
      if (cb.checked) {
        if (!filters.project.includes(p)) filters.project.push(p);
      } else {
        filters.project = filters.project.filter((x) => x !== p);
      }
      updateProjectLabel();
      refresh();
    });
    const text = document.createElement("span");
    text.textContent = p;
    opt.appendChild(cb);
    opt.appendChild(text);
    projectMs.panel.appendChild(opt);
  }
  updateProjectLabel();
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
  const axisFmt = (v) =>
    v >= 1e6 ? (v / 1e6).toFixed(0) + "M" : v >= 1e3 ? (v / 1e3).toFixed(0) + "k" : v;
  chart("chart-daily-cache").setOption({
    grid: { left: 60, right: 60, top: 30, bottom: 30 },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter: (params) => {
        const create = params.find((p) => p.seriesIndex === 0)?.value || 0;
        const read = params.find((p) => p.seriesIndex === 1)?.value || 0;
        const ratio = create ? (read / create).toFixed(0) + "×" : "—";
        return `${params[0].name}<br/>` +
          `<span style="color:#ffaa3a">●</span> ${t("series_cache_create")}: ${fmt(create)}<br/>` +
          `<span style="color:#6cbf6c">●</span> ${t("series_cache_read")}: ${fmt(read)}<br/>` +
          `<span style="color:#888">${t("cache_ratio_label")}: ${ratio}</span>`;
      },
    },
    legend: { top: 0, textStyle: { color: "#aaa" } },
    xAxis: { type: "category", data: data.map((d) => d.day) },
    yAxis: [
      {
        type: "value",
        position: "left",
        nameTextStyle: { color: "#ffaa3a" },
        axisLabel: { color: "#ffaa3a", formatter: axisFmt },
        splitLine: { lineStyle: { color: "#222" } },
      },
      {
        type: "value",
        position: "right",
        nameTextStyle: { color: "#6cbf6c" },
        axisLabel: { color: "#6cbf6c", formatter: axisFmt },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: t("series_cache_create"),
        type: "bar",
        yAxisIndex: 0,
        data: data.map((d) => d.cache_create_tokens),
        itemStyle: { color: "#ffaa3a" },
      },
      {
        name: t("series_cache_read"),
        type: "bar",
        yAxisIndex: 1,
        data: data.map((d) => d.cache_read_tokens),
        itemStyle: { color: "#6cbf6c" },
      },
    ],
  });
}

async function loadByProject() {
  const box = document.getElementById("chart-by-project").closest(".chart-box");
  // Tautological when filtered to a single project — hide the card entirely.
  if (filters.project.length === 1) {
    box.classList.add("hidden");
    // Neighbor expands via CSS :has(); resize it after layout.
    requestAnimationFrame(() => charts["chart-by-model"]?.resize());
    return;
  }
  box.classList.remove("hidden");
  const r = await fetch("/api/by-project" + qs());
  const data = await r.json();
  // Concurrent clicks can leave the canvas out of sync with the container.
  // Wait one frame so any pending layout settles, then force a resize before
  // drawing — otherwise ECharts may keep stale dimensions captured while the
  // card was hidden.
  await new Promise((r) => requestAnimationFrame(r));
  const c = chart("chart-by-project");
  c.resize();
  charts["chart-by-model"]?.resize();
  c.setOption({
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
    grid: { left: 210, right: 60, top: 20, bottom: 30 },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter: (p) => `${p[0].name}<br/>${fmt(p[0].value)} ${t("chart_tool_uses_in")} ${reversed[p[0].dataIndex].sessions} ${t("chart_tool_sessions_word")}`,
    },
    yAxis: {
      type: "category",
      data: reversed.map((d) => d.tool_name),
      axisLabel: {
        color: "#aaa",
        // Names like "chrome-devtools__take_snapshot" overflow the gutter;
        // truncate visually — full name is still in the tooltip.
        formatter: (name) => (name.length > 28 ? name.slice(0, 26) + "…" : name),
      },
    },
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
  const r = await fetch("/api/sessions?limit=8" + (qs() && "&" + qs().slice(1)));
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
