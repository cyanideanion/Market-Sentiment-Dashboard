'use strict';
const statusBox = document.querySelector('#status');
let dashboard;
const rendered = new Map();
const tabs = [...document.querySelectorAll('[role="tab"]')];
const errorText = err => err instanceof Error ? err.message : String(err);

async function readJSON(url) {
  const response = await fetch(url, {cache: 'no-store'});
  if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
  return response.json();
}
function setBadge(node, label) {
  node.textContent = label;
  node.classList.remove('fear', 'greed', 'neutral');
  node.classList.add(label.includes('Fear') ? 'fear' : label.includes('Greed') ? 'greed' : 'neutral');
}
function loadPlotly(version) {
  if (!/^\d+\.\d+\.\d+$/.test(version)) throw new Error('Invalid Plotly version in summary.json.');
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = `https://cdn.plot.ly/plotly-${version}.min.js`;
    script.onload = resolve;
    script.onerror = () => reject(new Error('The chart library could not load. Check your internet connection and reload.'));
    document.head.append(script);
  });
}
// Only bold markup and paragraphs/lists are needed by the existing commentary.
// Text is added through textContent, never inserted as executable HTML.
function inlineText(node, text) {
  text.split(/(\*\*[^*]+\*\*)/g).forEach(piece => {
    const child = document.createElement(piece.startsWith('**') ? 'strong' : 'span');
    child.textContent = piece.startsWith('**') ? piece.slice(2, -2) : piece;
    node.append(child);
  });
}
function prose(node, text) {
  String(text).trim().split(/\n\s*\n/).forEach(block => {
    const value = block.trim().replace(/\s*\n\s*/g, ' ');
    const element = document.createElement(value.startsWith('- ') ? 'ul' : 'p');
    if (value.startsWith('- ')) { const li = document.createElement('li'); inlineText(li, value.slice(2)); element.append(li); }
    else inlineText(element, value);
    node.append(element);
  });
}
async function loadContent() {
  const content = await readJSON('content.json');
  document.querySelectorAll('[data-description]').forEach(node => { node.textContent = content.indicators[node.dataset.description]; });
  document.querySelectorAll('[data-research]').forEach(node => {
    const section = content.research[node.dataset.research];
    prose(node, section.method);
    const details = document.createElement('details');
    const title = document.createElement('summary'); title.textContent = 'Read findings and discussion'; details.append(title);
    prose(details, section.results); prose(details, section.discussion); node.append(details);
  });
}
async function renderChart(node) {
  const key = node.dataset.chart;
  if (rendered.has(key)) return rendered.get(key);
  const task = (async () => {
    const entry = dashboard.charts[key];
    if (!entry || entry.status !== 'ready') {
      node.textContent = entry?.reason || 'This chart is unavailable for this update.';
      node.classList.add('chart-error'); return;
    }
    if (!/^[a-z_]+\.json$/.test(entry.file)) throw new Error(`Invalid chart filename: ${key}`);
    const fig = await readJSON(`data/${entry.file}`);
    const mobile = window.innerWidth < 800;
    const layout = {...fig.layout, autosize: true, paper_bgcolor: '#ffffff', plot_bgcolor: '#ffffff',
      font: {...fig.layout.font, family: 'system-ui, sans-serif', color: '#334b55', size: mobile ? 10 : 12},
      margin: {l: mobile ? 45 : 60, r: 24, t: 100, b: 65},
      height: key === 'correlation' ? 650 : key === 'recovery' || key === 'forward_returns' ? 560 : mobile ? 400 : 460};
    delete layout.width;
    // Section headings supply titles; omitting repeated Plotly titles avoids clipping.
    layout.title = {text: ''};
    await Plotly.newPlot(node, fig.data, layout, {responsive: true, displayModeBar: true, displaylogo: false, scrollZoom: false});
  })().catch(err => { node.textContent = `Chart could not load: ${errorText(err)}`; node.classList.add('chart-error'); console.error(err); });
  rendered.set(key, task); return task;
}
async function renderVisible() {
  if (!dashboard || !window.Plotly) return;
  const nodes = [...document.querySelectorAll('[data-chart]')].filter(node => !node.closest('[hidden]'));
  await Promise.all(nodes.map(renderChart));
  nodes.filter(n => n.classList.contains('js-plotly-plot')).forEach(n => Plotly.Plots.resize(n));
}
function selectTab(tab, focus = false) {
  tabs.forEach(button => {
    const active = button === tab;
    button.setAttribute('aria-selected', String(active)); button.tabIndex = active ? 0 : -1;
    document.getElementById(button.getAttribute('aria-controls')).hidden = !active;
  });
  if (focus) tab.focus();
  renderVisible();
}
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectTab(tab));
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next !== undefined) { event.preventDefault(); selectTab(tabs[next], true); }
  });
});
(async () => {
  if (location.protocol === 'file:') { statusBox.className = 'error'; statusBox.textContent = 'Open this dashboard through a local web server, rather than double-clicking index.html. See START_HERE.md.'; return; }
  try {
    dashboard = await readJSON('data/summary.json');
    if (dashboard.schema_version !== 1) throw new Error('Unsupported dashboard data format.');
    document.querySelector('#overall-score').textContent = Math.round(dashboard.overall.score);
    setBadge(document.querySelector('#overall-label'), dashboard.overall.label);
    document.querySelector('#market-date').textContent = `Market data: ${dashboard.overall.market_data_date}`;
    document.querySelector('#updated').textContent = `Last updated: ${new Date(dashboard.generated_at_utc).toLocaleString(undefined, {dateStyle:'medium',timeStyle:'short'})} (local time)`;
    document.querySelectorAll('[data-indicator]').forEach(node => {
      const value = dashboard.indicators[node.dataset.indicator];
      setBadge(node, value.label); node.title = `Score: ${value.score.toFixed(1)} / 100 · Data: ${value.market_data_date}`;
    });
    const contentTask = loadContent().catch(err => { statusBox.textContent = 'Some explanatory text could not load. Reload to retry.'; console.error(err); return false; });
    await loadPlotly(dashboard.plotly_js_version);
    await renderVisible();
    if (await contentTask !== false) statusBox.hidden = true;
  } catch (err) {
    statusBox.className = 'error';
    statusBox.textContent = `Dashboard could not load. ${errorText(err)} Check that build_dashboard.py completed and site/data contains its output.`;
  }
})();
