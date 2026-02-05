/**
 * BIM Ontology Dashboard - Main Application
 */

const API_BASE = '';  // Same origin
let currentPage = 0;
const PAGE_SIZE = 50;
let categoryChart = null;
let barChart = null;
const DEFAULT_MAX_LEVEL = 10;
const SYSTEM_DEPTH_LABELS = { 1: 'Project', 2: 'Area', 3: 'Unit', 4: 'System' };
let metadataCache = { maxLevel: null, totalObjects: null, totalProps: null };
const tabState = {};
let activeTabName = 'overview';

// ── Navigation ──

function ensureTabState(tabName) {
    if (!tabState[tabName]) {
        tabState[tabName] = {
            initialized: false,
            scrollTop: 0,
            scrolls: {},
            formValues: {},
            page: null,
            drillPaths: [],
        };
    }
    return tabState[tabName];
}

function captureFormState(tabEl) {
    const values = {};
    tabEl.querySelectorAll('input, select, textarea').forEach(el => {
        if (!el.id) return;
        if (el.type === 'checkbox' || el.type === 'radio') values[el.id] = el.checked;
        else values[el.id] = el.value;
    });
    return values;
}

function restoreFormState(tabEl, values) {
    if (!values) return;
    Object.entries(values).forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (!el || !tabEl.contains(el)) return;
        if (el.type === 'checkbox' || el.type === 'radio') el.checked = Boolean(value);
        else el.value = value;
    });
}

function saveTabState(tabName) {
    if (!tabName) return;
    const tabEl = document.getElementById('tab-' + tabName);
    if (!tabEl) return;

    const state = ensureTabState(tabName);
    state.formValues = captureFormState(tabEl);
    state.scrollTop = window.scrollY || document.documentElement.scrollTop || document.body.scrollTop || 0;
    state.scrolls = {};
    tabEl.querySelectorAll('[data-scroll-id]').forEach(el => {
        state.scrolls[el.dataset.scrollId] = { top: el.scrollTop, left: el.scrollLeft };
    });

    if (tabName === 'elements') {
        state.page = currentPage;
    }
    if (tabName === 'hierarchy') {
        state.navisDrillUris = navisDrillState.selectedUris.slice();
    }
}

function restoreTabState(tabName) {
    const state = ensureTabState(tabName);
    const tabEl = document.getElementById('tab-' + tabName);
    if (!tabEl) return;

    restoreFormState(tabEl, state.formValues);

    if (tabName === 'elements' && Number.isFinite(state.page)) {
        currentPage = state.page;
    }
    if (tabName === 'hierarchy' && Array.isArray(state.navisDrillUris)) {
        navisDrillState.selectedUris = state.navisDrillUris.slice();
        if (navisDrillData) renderNavisDrilldown();
    }

    requestAnimationFrame(() => {
        if (Number.isFinite(state.scrollTop)) window.scrollTo(0, state.scrollTop);
        tabEl.querySelectorAll('[data-scroll-id]').forEach(el => {
            const pos = state.scrolls?.[el.dataset.scrollId];
            if (!pos) return;
            el.scrollTop = pos.top || 0;
            el.scrollLeft = pos.left || 0;
        });
    });
}

function initializeTab(tabName) {
    const state = ensureTabState(tabName);
    if (state.initialized) return;

    if (tabName === 'buildings') loadHierarchy();
    if (tabName === 'hierarchy') initHierarchyTab();
    if (tabName === 'elements') { loadCategoryFilter(); loadElements(); }
    if (tabName === 'properties') loadPlantData();
    if (tabName === 'ontology') { loadOntologyTypes(); loadOntologyLinks(); loadRules(); }
    if (tabName === 'validation') loadTTLFiles();
    if (tabName === 'explorer') initExplorer();
    if (tabName === 'lean') loadLeanStats();
    if (tabName === 'todayswork') initTodaysWork();
    if (tabName === 'statusmon') initStatusMonitor();

    state.initialized = true;
}

function setActiveTabUI(tabName) {
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
    const tab = document.querySelector(`.nav-tab[data-tab="${tabName}"]`);
    if (tab) tab.classList.add('active');
    const target = document.getElementById('tab-' + tabName);
    if (target) target.style.display = 'block';
}

function switchTab(tabName) {
    if (!tabName || tabName === activeTabName) return;
    saveTabState(activeTabName);
    setActiveTabUI(tabName);
    activeTabName = tabName;

    const state = ensureTabState(tabName);
    if (!state.initialized) initializeTab(tabName);
    else restoreTabState(tabName);
}

document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
});

// ── API Helpers ──

async function api(path, opts = {}) {
    try {
        const res = await fetch(API_BASE + path, opts);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (e) {
        console.error('API error:', path, e);
        return null;
    }
}

async function apiPost(path, body) {
    return api(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
}

function formatNumber(n) {
    if (n == null) return '--';
    return n.toLocaleString();
}

function formatDecimal(n, digits = 2) {
    if (n == null) return '--';
    const num = Number(n);
    if (!Number.isFinite(num)) return '--';
    return num.toLocaleString(undefined, {
        minimumFractionDigits: digits,
        maximumFractionDigits: digits,
    });
}

function coerceInt(value) {
    const n = parseInt(value, 10);
    return Number.isFinite(n) ? n : null;
}

function updateDepthSelector(selectId, maxLevel, options_config = {}) {
    const select = document.getElementById(selectId);
    if (!select) return;

    const { labelMap = null, preferredValue = null, startAt = 1 } = options_config;
    const currentValue = coerceInt(select.value);
    const targetLevel = Number.isFinite(maxLevel) && maxLevel > 0 ? maxLevel : DEFAULT_MAX_LEVEL;

    let options = '';
    for (let i = startAt; i <= targetLevel; i++) {
        const label = labelMap && labelMap[i] ? `Depth ${i} (${labelMap[i]})` : `Depth ${i}`;
        options += `<option value="${i}">${label}</option>`;
    }
    select.innerHTML = options;
    select.disabled = false;

    const defaultVal = preferredValue != null ? Math.min(preferredValue, targetLevel) : targetLevel;
    const nextValue = currentValue && currentValue >= startAt && currentValue <= targetLevel
        ? currentValue
        : defaultVal;
    select.value = nextValue;
}

function updateDepthSelectors(maxLevel) {
    // System Path: max 4 levels (Project/Area/Unit/System), default 3
    updateDepthSelector('hierarchy-depth', Math.min(maxLevel || 4, 4), { labelMap: SYSTEM_DEPTH_LABELS, preferredValue: 3 });
    // Navisworks: full depth range, default to max
    updateDepthSelector('navis-depth', maxLevel, { preferredValue: null });
}

function updateBadgeText(elementId, label, value) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const text = value == null ? '--' : formatNumber(value);
    el.textContent = `${label}: ${text}`;
}

function updateMetadataUI() {
    const maxLevel = metadataCache.maxLevel;
    const totalProps = metadataCache.totalProps;
    const totalObjects = metadataCache.totalObjects;
    const displayMaxLevel = maxLevel && maxLevel > 0 ? maxLevel : null;

    const maxLevelBadge = document.getElementById('overview-max-level');
    const maxLevelStat = document.getElementById('stat-max-level');
    const propStat = document.getElementById('stat-properties');

    if (maxLevelBadge) {
        maxLevelBadge.textContent = displayMaxLevel == null ? '--' : `Level ${displayMaxLevel}`;
        maxLevelBadge.title = `Objects: ${formatNumber(totalObjects || 0)}, Properties: ${formatNumber(totalProps || 0)}`;
    }
    if (maxLevelStat) {
        maxLevelStat.textContent = displayMaxLevel == null ? '--' : displayMaxLevel;
    }
    if (propStat) {
        propStat.textContent = totalProps == null ? '--' : formatNumber(totalProps);
    }

    updateDepthSelectors(maxLevel);
    updateBadgeText('hierarchy-max-level', 'Max Level', displayMaxLevel);
    updateBadgeText('hierarchy-prop-count', 'Property Values', totalProps);
    updateBadgeText('exp-max-level', 'Max Level', displayMaxLevel);
    updateBadgeText('exp-prop-count', 'Property Values', totalProps);
}

// ── Health & Init ──

async function checkHealth() {
    const data = await api('/health');
    const el = document.getElementById('health-indicator');
    const tc = document.getElementById('triple-count');
    if (data && data.status === 'healthy') {
        el.textContent = 'Connected';
        el.style.color = '#4ade80';
        tc.textContent = formatNumber(data.triples) + ' triples';
    } else {
        el.textContent = 'Disconnected';
        el.style.color = '#ef4444';
    }
}

// ── Overview Tab ──

let overviewFilesLoaded = false;

async function loadOverviewFiles() {
    if (overviewFilesLoaded) return;

    const select = document.getElementById('overview-file-select');
    const data = await api('/api/reasoning/ttl-files');

    if (!data || !data.files) {
        select.innerHTML = '<option value="">Failed to load files</option>';
        return;
    }

    // Sort files: v3 first, then by name
    const sortedFiles = data.files
        .filter(f => f.name.endsWith('.ttl'))
        .sort((a, b) => {
            if (a.name.includes('-v3')) return -1;
            if (b.name.includes('-v3')) return 1;
            return b.size_kb - a.size_kb;  // Larger files first
        });

    select.innerHTML = sortedFiles
        .map(f => {
            const label = f.name.includes('-v3') ? `${f.name} [Full Properties]` : f.name;
            const selected = f.name.includes('-v3') ? 'selected' : '';
            return `<option value="${f.name}" ${selected}>${label} (${f.size_kb} KB)</option>`;
        })
        .join('');

    overviewFilesLoaded = true;
}

async function loadOverviewFile() {
    const select = document.getElementById('overview-file-select');
    const status = document.getElementById('overview-file-status');
    const fileName = select.value;

    if (!fileName) {
        status.textContent = 'Please select a file';
        status.style.color = '#f87171';
        return;
    }

    status.textContent = 'Loading graph...';
    status.style.color = '#94a3b8';

    try {
        const data = await apiPost(`/api/reasoning/reload?file_name=${encodeURIComponent(fileName)}`, {});

        if (data && data.status === 'success') {
            status.textContent = `Loaded: ${formatNumber(data.triples)} triples`;
            status.style.color = '#4ade80';

            // Refresh all data
            checkHealth();
            loadOverview();
            loadMaxLevel();

            // Sync hierarchy file select if on that tab
            const hierSelect = document.getElementById('hierarchy-file-select');
            if (hierSelect) hierSelect.value = fileName;
        } else {
            status.textContent = `Error: ${data?.detail || 'Unknown'}`;
            status.style.color = '#f87171';
        }
    } catch (e) {
        status.textContent = `Error: ${e.message}`;
        status.style.color = '#f87171';
    }
}

async function loadMaxLevel() {
    const query = `
PREFIX navis: <http://example.org/bim-ontology/navis#>
SELECT ?maxLevel ?totalObjects ?totalProps WHERE {
    ?meta navis:maxHierarchyLevel ?maxLevel .
    OPTIONAL { ?meta navis:totalObjects ?totalObjects }
    OPTIONAL { ?meta navis:totalPropertyValues ?totalProps }
}`;

    const data = await apiPost('/api/sparql', { query });
    if (data && data.results && data.results.length > 0) {
        const r = data.results[0];
        metadataCache = {
            maxLevel: coerceInt(r.maxLevel),
            totalObjects: coerceInt(r.totalObjects),
            totalProps: coerceInt(r.totalProps),
        };
        updateMetadataUI();
    } else {
        metadataCache = { maxLevel: null, totalObjects: null, totalProps: null };
        updateMetadataUI();
    }
}

async function loadOverview() {
    const stats = await api('/api/statistics');
    if (stats) {
        document.getElementById('stat-triples').textContent = formatNumber(stats.total_triples);
        document.getElementById('stat-elements').textContent = formatNumber(stats.total_elements);
        document.getElementById('stat-buildings').textContent = formatNumber(stats.buildings);
        document.getElementById('stat-categories').textContent = formatNumber(stats.total_categories);
    }

    const cats = await api('/api/statistics/categories');
    if (cats && cats.length > 0) {
        renderCategoryChart(cats);
        renderBarChart(cats);
    }
}

function renderCategoryChart(cats) {
    const ctx = document.getElementById('chart-categories').getContext('2d');
    const colors = [
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
        '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
        '#14b8a6', '#a855f7', '#d946ef', '#0ea5e9', '#22c55e',
        '#eab308', '#e11d48', '#7c3aed'
    ];

    if (categoryChart) categoryChart.destroy();
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: cats.map(c => c.category),
            datasets: [{
                data: cats.map(c => c.count),
                backgroundColor: colors.slice(0, cats.length),
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: '#94a3b8', font: { size: 11 }, padding: 8 }
                }
            }
        }
    });
}

function renderBarChart(cats) {
    const ctx = document.getElementById('chart-bar').getContext('2d');
    const top10 = cats.slice(0, 10);

    if (barChart) barChart.destroy();
    barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: top10.map(c => c.category),
            datasets: [{
                label: 'Element Count',
                data: top10.map(c => c.count),
                backgroundColor: '#3b82f6',
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } },
                y: { ticks: { color: '#94a3b8', font: { size: 11 } }, grid: { display: false } }
            }
        }
    });
}

// ── Buildings Tab ──

async function loadHierarchy() {
    const container = document.getElementById('hierarchy-tree');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading building hierarchy...</div>';
    const data = await api('/api/hierarchy');
    if (!data) {
        container.innerHTML = '<p class="text-gray-500 text-sm">Failed to load building hierarchy. Check the data source.</p>';
        return;
    }

    container.innerHTML = '';
    renderHierarchyNodes(container, data, 0);
}

function renderHierarchyNodes(parent, nodes, depth) {
    if (!nodes || !Array.isArray(nodes)) {
        if (nodes && nodes.name) nodes = [nodes];
        else return;
    }

    nodes.forEach(node => {
        const div = document.createElement('div');
        div.className = 'hierarchy-node';

        const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
        const typeLabels = { Project: 'PRJ', Site: 'SITE', Building: 'BLD', BuildingStorey: 'STY', Space: 'SPC' };
        const typeColors = { Project: '#8b5cf6', Site: '#10b981', Building: '#3b82f6', BuildingStorey: '#f59e0b', Space: '#06b6d4' };

        const nodeType = node.type || '';
        const shortType = typeLabels[nodeType] || nodeType.substring(0, 3).toUpperCase();
        const color = typeColors[nodeType] || colors[depth % colors.length];

        const header = document.createElement('div');
        header.className = 'flex items-center gap-2 py-1 px-2 rounded cursor-pointer hover:bg-gray-800';
        header.innerHTML = `
            <span class="node-icon" style="background:${color}"></span>
            <span class="text-sm">${node.name || 'Unnamed'}</span>
            <span class="badge" style="background:${color}22;color:${color}">${shortType}</span>
            ${node.element_count ? `<span class="text-xs text-gray-500">(${node.element_count})</span>` : ''}
        `;
        header.addEventListener('click', () => loadStoreyDetail(node));
        div.appendChild(header);

        if (node.children && node.children.length > 0) {
            const children = document.createElement('div');
            children.className = 'children';
            renderHierarchyNodes(children, node.children, depth + 1);
            div.appendChild(children);
        }

        parent.appendChild(div);
    });
}

async function loadStoreyDetail(node) {
    const container = document.getElementById('storey-detail');
    container.innerHTML = `
        <h3 class="text-lg font-semibold mb-3">${node.name || 'Unnamed'} <span class="badge badge-blue">${node.type || ''}</span></h3>
        ${node.global_id ? `<p class="text-xs text-gray-500 mb-3">GlobalId: ${node.global_id}</p>` : ''}
    `;

    // Load storeys for this building
    const storeys = await api('/api/storeys');
    if (storeys && storeys.length > 0) {
        let html = '<table><thead><tr><th>Storey</th><th>Elevation</th></tr></thead><tbody>';
        storeys.forEach(s => {
            html += `<tr><td>${s.name || 'Unnamed'}</td><td>${s.elevation != null ? s.elevation.toFixed(1) + 'm' : '-'}</td></tr>`;
        });
        html += '</tbody></table>';
        container.innerHTML += html;
    }
}

// ── Elements Tab ──

let allCategories = [];

async function loadCategoryFilter() {
    if (allCategories.length > 0) return;
    const cats = await api('/api/statistics/categories');
    if (cats) {
        allCategories = cats;
        const select = document.getElementById('filter-category');
        cats.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.category;
            opt.textContent = `${c.category} (${c.count})`;
            select.appendChild(opt);
        });
    }
}

async function loadElements() {
    const category = document.getElementById('filter-category').value;
    const search = document.getElementById('filter-search').value;
    const tbody = document.getElementById('elements-table');
    tbody.innerHTML = '<tr><td colspan="4" class="loading"><div class="spinner"></div>Loading elements...</td></tr>';

    let url = `/api/elements?limit=${PAGE_SIZE}&offset=${currentPage * PAGE_SIZE}`;
    if (category) url += `&category=${encodeURIComponent(category)}`;

    const data = await api(url);
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-gray-500">No elements found. Try a different category or clear the search.</td></tr>';
        document.getElementById('elements-info').textContent = '0 elements';
        return;
    }

    // Client-side name filter
    let filtered = data;
    if (search) {
        const q = search.toLowerCase();
        filtered = data.filter(e => (e.name || '').toLowerCase().includes(q));
    }

    tbody.innerHTML = filtered.map(e => `
        <tr>
            <td>${e.name || '<em class="text-gray-500">unnamed</em>'}</td>
            <td><span class="badge badge-blue">${e.category || '-'}</span></td>
            <td class="text-gray-400">${e.original_type || '-'}</td>
            <td class="text-gray-500 text-xs font-mono">${e.global_id || '-'}</td>
        </tr>
    `).join('');

    document.getElementById('elements-info').textContent =
        `Showing ${filtered.length} elements (page ${currentPage + 1})`;
}

function nextPage() { currentPage++; loadElements(); }
function prevPage() { if (currentPage > 0) { currentPage--; loadElements(); } }

// ── SPARQL Tab ──

const QUERY_TEMPLATES = [
    {
        name: 'Category Statistics',
        query: `PREFIX bim: <http://example.org/bim-ontology/schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?cat (COUNT(?e) AS ?num)
WHERE {
    ?e rdf:type bim:PhysicalElement .
    ?e bim:hasCategory ?cat .
}
GROUP BY ?cat
ORDER BY DESC(?num)`
    },
    {
        name: 'Building Hierarchy',
        query: `PREFIX bim: <http://example.org/bim-ontology/schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?parent_name ?child_name
WHERE {
    ?parent bim:aggregates ?child .
    ?parent bim:hasName ?parent_name .
    ?child bim:hasName ?child_name .
}`
    },
    {
        name: 'Elements by Storey',
        query: `PREFIX bim: <http://example.org/bim-ontology/schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?storey_name (COUNT(?elem) AS ?num)
WHERE {
    ?storey a bim:BuildingStorey .
    ?storey bim:hasName ?storey_name .
    ?storey bim:containsElement ?elem .
}
GROUP BY ?storey_name`
    },
    {
        name: 'Pipe Elements',
        query: `PREFIX bim: <http://example.org/bim-ontology/schema#>

SELECT ?name ?type
WHERE {
    ?e bim:hasCategory "Pipe" .
    ?e bim:hasName ?name .
    OPTIONAL { ?e bim:hasObjectType ?type }
}
LIMIT 20`
    },
    {
        name: 'All Properties of Element',
        query: `PREFIX bim: <http://example.org/bim-ontology/schema#>

SELECT ?prop ?value
WHERE {
    ?e bim:hasName "YOUR_ELEMENT_NAME" .
    ?e ?prop ?value .
}
LIMIT 50`
    },
    {
        name: 'Structural Elements (after reasoning)',
        query: `PREFIX bim: <http://example.org/bim-ontology/schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?name ?cat
WHERE {
    ?e rdf:type bim:StructuralElement .
    ?e bim:hasName ?name .
    ?e bim:hasCategory ?cat .
}
LIMIT 30`
    },
    {
        name: 'Delivery Status Summary',
        query: `PREFIX bim: <http://example.org/bim-ontology/schema#>

SELECT ?status (COUNT(?e) AS ?count)
WHERE {
    ?e bim:hasDeliveryStatus ?status .
}
GROUP BY ?status
ORDER BY DESC(?count)`
    },
    {
        name: 'Today\'s Work (AWP)',
        query: `PREFIX awp: <http://example.org/bim-ontology/awp#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?iwp ?label ?start ?end ?constraint
WHERE {
    ?iwp a awp:InstallationWorkPackage .
    ?iwp rdfs:label ?label .
    OPTIONAL { ?iwp awp:hasStartDate ?start }
    OPTIONAL { ?iwp awp:hasEndDate ?end }
    OPTIONAL { ?iwp awp:hasConstraintStatus ?constraint }
}
ORDER BY ?start`
    },
    {
        name: 'Delayed Elements',
        query: `PREFIX bim: <http://example.org/bim-ontology/schema#>
PREFIX sched: <http://example.org/bim-ontology/schedule#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?name ?category ?plannedDate ?deliveryStatus
WHERE {
    ?e a bim:PhysicalElement .
    ?e sched:hasPlannedInstallDate ?plannedDate .
    ?e bim:hasDeliveryStatus ?deliveryStatus .
    OPTIONAL { ?e bim:hasName ?name }
    OPTIONAL { ?e bim:hasCategory ?category }
    FILTER(?deliveryStatus NOT IN ("Installed", "Inspected"))
}
ORDER BY ?plannedDate
LIMIT 50`
    },
    {
        name: 'AWP Hierarchy (CWA > CWP > IWP)',
        query: `PREFIX awp: <http://example.org/bim-ontology/awp#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?cwa ?cwp ?iwp
WHERE {
    ?iwpNode a awp:InstallationWorkPackage .
    ?iwpNode rdfs:label ?iwp .
    OPTIONAL {
        ?iwpNode awp:belongsToCWP ?cwpNode .
        ?cwpNode rdfs:label ?cwp .
        OPTIONAL {
            ?cwpNode awp:belongsToCWA ?cwaNode .
            ?cwaNode rdfs:label ?cwa .
        }
    }
}
ORDER BY ?cwa ?cwp ?iwp`
    },
];

function initQueryTemplates() {
    const container = document.getElementById('query-templates');
    QUERY_TEMPLATES.forEach(t => {
        const btn = document.createElement('button');
        btn.className = 'btn btn-secondary w-full text-left text-sm';
        btn.textContent = t.name;
        btn.addEventListener('click', () => {
            document.getElementById('sparql-editor').value = t.query;
        });
        container.appendChild(btn);
    });
}

async function executeSparql() {
    const query = document.getElementById('sparql-editor').value.trim();
    if (!query) return;

    const thead = document.getElementById('sparql-thead');
    const tbody = document.getElementById('sparql-tbody');
    const info = document.getElementById('sparql-info');

    tbody.innerHTML = '<tr><td class="loading"><div class="spinner"></div>Executing...</td></tr>';

    const start = performance.now();
    const data = await apiPost('/api/sparql', { query });
    const elapsed = performance.now() - start;

    if (!data || !data.results) {
        tbody.innerHTML = '<tr><td class="text-red-400">Query failed. Check syntax.</td></tr>';
        info.textContent = `Error (${elapsed.toFixed(0)}ms)`;
        return;
    }

    const results = data.results;
    if (results.length === 0) {
        thead.innerHTML = '<tr><th>--</th></tr>';
        tbody.innerHTML = '<tr><td class="text-gray-500">No results.</td></tr>';
        info.textContent = `0 rows (${elapsed.toFixed(0)}ms)`;
        return;
    }

    const columns = Object.keys(results[0]);
    thead.innerHTML = '<tr>' + columns.map(c => `<th>${c}</th>`).join('') + '</tr>';
    tbody.innerHTML = results.map(row =>
        '<tr>' + columns.map(c => {
            let val = row[c];
            if (typeof val === 'string' && val.startsWith('http://')) {
                val = val.split('#').pop() || val.split('/').pop() || val;
            }
            return `<td>${val != null ? val : ''}</td>`;
        }).join('') + '</tr>'
    ).join('');

    info.textContent = `${results.length} rows (${elapsed.toFixed(0)}ms)`;
}

// ── Reasoning Tab ──

async function runReasoning() {
    const btn = document.getElementById('btn-reasoning');
    const status = document.getElementById('reasoning-status');
    btn.disabled = true;
    btn.textContent = 'Running...';
    status.innerHTML = '<div class="loading"><div class="spinner"></div>Applying OWL/RDFS reasoning rules...</div>';

    const data = await apiPost('/api/reasoning', {});

    btn.disabled = false;
    btn.textContent = 'Run Reasoning';

    if (!data || data.error) {
        status.innerHTML = `<p class="text-red-400">${data?.error || 'Reasoning failed.'}</p>`;
        return;
    }

    status.innerHTML = `
        <p class="text-green-400 font-semibold mb-2">Reasoning completed successfully.</p>
        <p class="text-sm text-gray-400">Rules applied: ${(data.rules_applied || []).join(', ')}</p>
    `;

    document.getElementById('reason-before').textContent = formatNumber(data.total_triples - data.total_inferred);
    document.getElementById('reason-after').textContent = formatNumber(data.total_triples);
    document.getElementById('reason-inferred').textContent = '+' + formatNumber(data.total_inferred);
    document.getElementById('reason-time').textContent = (data.elapsed || 0).toFixed(1) + 's';

    // Refresh overview stats
    checkHealth();

    // Query inferred types
    const typesContainer = document.getElementById('reasoning-types');
    const typeData = await apiPost('/api/sparql', {
        query: `PREFIX bim: <http://example.org/bim-ontology/schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?type (COUNT(?e) AS ?num) WHERE {
    VALUES ?type { bim:StructuralElement bim:MEPElement bim:AccessElement }
    ?e rdf:type ?type .
} GROUP BY ?type ORDER BY DESC(?num)`
    });

    if (typeData && typeData.results && typeData.results.length > 0) {
        let html = '<table><thead><tr><th>Inferred Type</th><th>Count</th></tr></thead><tbody>';
        typeData.results.forEach(r => {
            const typeName = (r.type || '').split('#').pop();
            html += `<tr><td><span class="badge badge-green">${typeName}</span></td><td>${r.num}</td></tr>`;
        });
        html += '</tbody></table>';
        typesContainer.innerHTML = html;
    }
}

// ── Properties Tab ──

async function lookupProperties() {
    const gid = document.getElementById('prop-global-id').value.trim();
    if (!gid) return;
    const container = document.getElementById('prop-results');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading properties...</div>';

    const data = await api(`/api/properties/${encodeURIComponent(gid)}`);
    if (!data || data.detail) {
        container.innerHTML = `<p class="text-red-400 text-sm">${data?.detail || 'Not found'}</p>`;
        return;
    }

    let html = '';
    (data.property_sets || []).forEach(pset => {
        html += `<div class="mb-4"><h4 class="text-sm font-semibold text-blue-400 mb-1">${pset.name}</h4><table><tbody>`;
        Object.entries(pset.properties || {}).forEach(([k, v]) => {
            html += `<tr><td class="text-gray-400">${k}</td><td>${v != null ? v : '<em class="text-gray-600">null</em>'}</td></tr>`;
        });
        html += '</tbody></table></div>';
    });
    container.innerHTML = html || '<p class="text-gray-500 text-sm">No properties found.</p>';
}

async function searchProperties() {
    const key = document.getElementById('prop-search-key').value.trim();
    if (!key) return;
    const container = document.getElementById('prop-results');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Searching properties...</div>';

    const data = await api(`/api/properties/search?key=${encodeURIComponent(key)}&limit=50`);
    if (!data || !data.results) {
        container.innerHTML = '<p class="text-gray-500 text-sm">No results. Try a shorter or different property key.</p>';
        return;
    }

    let html = `<p class="text-xs text-gray-500 mb-2">${data.count} results for "${key}"</p><table><thead><tr><th>Element</th><th>PropertySet</th><th>Value</th></tr></thead><tbody>`;
    data.results.forEach(r => {
        html += `<tr><td>${r.elem_name || '-'}</td><td>${r.pset_name || '-'}</td><td>${r.val != null ? r.val : '-'}</td></tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}

async function loadPlantData() {
    const container = document.getElementById('plant-data');
    const data = await api('/api/properties/plant-data');
    if (!data) {
        container.innerHTML = '<p class="text-gray-500 text-sm">Failed to load plant data.</p>';
        return;
    }

    let html = `<div class="grid grid-cols-2 gap-4 mb-4">
        <div><div class="stat-label">Total PropertySets</div><div class="text-2xl font-bold">${formatNumber(data.total_property_sets)}</div></div>
        <div><div class="stat-label">Plant (SP3D) PropertySets</div><div class="text-2xl font-bold text-green-400">${formatNumber(data.plant_property_sets)}</div></div>
    </div>`;

    if (data.plant_pset_details && data.plant_pset_details.length > 0) {
        html += '<table><thead><tr><th>PropertySet Name</th><th>Properties</th></tr></thead><tbody>';
        data.plant_pset_details.forEach(p => {
            html += `<tr><td>${p.pset_name}</td><td>${p.prop_count}</td></tr>`;
        });
        html += '</tbody></table>';
    }
    container.innerHTML = html;
}

// ── Ontology Editor Tab ──

async function loadOntologyTypes() {
    const container = document.getElementById('ontology-types');
    const data = await api('/api/ontology/types');
    if (!data) { container.innerHTML = '<p class="text-gray-500 text-sm">Failed to load.</p>'; return; }

    let html = '<table><thead><tr><th>Name</th><th>Parent</th><th>Label</th></tr></thead><tbody>';
    data.forEach(t => {
        html += `<tr><td><span class="badge badge-blue">${t.name}</span></td><td class="text-gray-400">${t.parent_class || '-'}</td><td>${t.label || '-'}</td></tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}

async function loadOntologyLinks() {
    const container = document.getElementById('ontology-links');
    const data = await api('/api/ontology/links');
    if (!data) { container.innerHTML = '<p class="text-gray-500 text-sm">Failed to load.</p>'; return; }

    let html = '<table><thead><tr><th>Name</th><th>Domain</th><th>Range</th><th>Inverse</th></tr></thead><tbody>';
    data.forEach(l => {
        html += `<tr><td><span class="badge badge-purple">${l.name}</span></td><td>${l.domain || '-'}</td><td>${l.range_class || '-'}</td><td class="text-gray-400">${l.inverse_name || '-'}</td></tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}

async function loadRules() {
    const data = await api('/api/ontology/rules');
    if (data) {
        document.getElementById('rules-editor').value = JSON.stringify(data, null, 2);
    }
}

async function saveRules() {
    const text = document.getElementById('rules-editor').value;
    try {
        const rules = JSON.parse(text);
        const data = await apiPost('/api/ontology/rules', { rules });
        if (data && data.updated) {
            alert('Classification rules saved successfully.');
        }
    } catch(e) {
        alert('Invalid JSON: ' + e.message);
    }
}

function showCreateTypeForm() {
    const name = prompt('Object Type name:');
    if (!name) return;
    const parent = prompt('Parent class (default: BIMElement):', 'BIMElement');
    apiPost('/api/ontology/types', { name, parent_class: parent || 'BIMElement', label: name }).then(() => loadOntologyTypes());
}

function showCreateLinkForm() {
    const name = prompt('Link Type name:');
    if (!name) return;
    const domain = prompt('Domain class:');
    const range = prompt('Range class:');
    if (!domain || !range) return;
    apiPost('/api/ontology/links', { name, domain, range_class: range }).then(() => loadOntologyLinks());
}

async function exportSchema() {
    const data = await api('/api/ontology/export');
    if (data && data.schema) {
        const blob = new Blob([data.schema], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = 'bim_schema.json'; a.click();
        URL.revokeObjectURL(url);
    }
}

function importSchemaPrompt() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const text = await file.text();
        await apiPost('/api/ontology/import', { schema: text });
        loadOntologyTypes();
        loadOntologyLinks();
        loadRules();
    };
    input.click();
}

async function applySchema() {
    const status = document.getElementById('schema-status');
    status.innerHTML = '<div class="loading"><div class="spinner"></div>Applying schema...</div>';
    const data = await apiPost('/api/ontology/apply', {});
    if (data) {
        status.innerHTML = `<p class="text-green-400">Schema applied: +${data.triples_added} triples (total: ${formatNumber(data.total_triples)})</p>`;
        checkHealth();
    } else {
        status.innerHTML = '<p class="text-red-400">Failed to apply schema.</p>';
    }
}

// ── Validation Tab ──

const CHECK_LABELS = {
    schema_completeness: 'Schema Completeness',
    spatial_hierarchy: 'Spatial Hierarchy',
    element_statistics: 'Element Statistics',
    uri_consistency: 'URI Consistency',
    property_set_coverage: 'PropertySet Coverage',
    required_properties: 'Required Properties',
    classification_quality: 'Classification Quality',
    relationship_integrity: 'Relationship Integrity',
};

const STATUS_BADGE = {
    pass: 'badge-green',
    warn: 'badge-amber',
    info: 'badge-blue',
    fail: 'badge-red',
};

let ttlFilesLoaded = false;

async function loadTTLFiles() {
    if (ttlFilesLoaded) return;
    const data = await api('/api/reasoning/ttl-files');
    if (!data) return;
    const select = document.getElementById('val-ttl-select');
    select.innerHTML = '';
    data.files.forEach(f => {
        const opt = document.createElement('option');
        opt.value = f.name;
        opt.textContent = `${f.name} (${f.size_kb} KB)`;
        if (f.name === data.current) opt.selected = true;
        select.appendChild(opt);
    });
    ttlFilesLoaded = true;

    // Build filter checkboxes
    const filters = document.getElementById('val-filters');
    filters.innerHTML = '<span class="text-xs text-gray-500" style="align-self:center">Show:</span>';
    Object.entries(CHECK_LABELS).forEach(([key, label]) => {
        const lbl = document.createElement('label');
        lbl.className = 'filter-check';
        lbl.innerHTML = `<input type="checkbox" checked data-check="${key}"> ${label}`;
        lbl.querySelector('input').addEventListener('change', filterValidationChecks);
        filters.appendChild(lbl);
    });
}

async function runValidation() {
    const btn = document.getElementById('btn-run-validation');
    const file = document.getElementById('val-ttl-select').value;
    const container = document.getElementById('val-checks');
    const placeholder = document.getElementById('val-placeholder');

    btn.disabled = true;
    btn.textContent = 'Validating...';
    container.innerHTML = '<div class="loading col-span-2"><div class="spinner"></div>Running 8 validation checks...</div>';
    document.getElementById('val-summary').style.display = 'none';

    const url = file
        ? `/api/reasoning/validation-report?ttl_file=${encodeURIComponent(file)}`
        : '/api/reasoning/validation-report';
    const data = await api(url);

    btn.disabled = false;
    btn.textContent = 'Run Validation';

    if (!data) {
        container.innerHTML = '<p class="text-red-400 col-span-2">Validation failed.</p>';
        return;
    }

    document.getElementById('val-time').textContent = `Completed in ${data.validation_time}s`;
    renderValidationReport(data);

    // Show Other explorer if Other elements exist
    var clsCheck = data.checks.find(function(c) { return c.name === 'classification_quality'; });
    var explorer = document.getElementById('val-other-explorer');
    if (clsCheck && clsCheck.details.other_count > 0) {
        explorer.style.display = 'block';
        otherPage = 0;
        loadOtherElements();
    } else {
        explorer.style.display = 'none';
    }
}

function renderValidationReport(data) {
    // Summary
    const summary = document.getElementById('val-summary');
    summary.style.display = 'grid';
    document.getElementById('val-total-triples').textContent = formatNumber(data.total_triples);
    document.getElementById('val-pass').textContent = data.summary.pass;
    document.getElementById('val-warn').textContent = data.summary.warn;
    document.getElementById('val-fail').textContent = data.summary.fail + (data.summary.info || 0);

    // Check cards
    const container = document.getElementById('val-checks');
    container.innerHTML = '';

    data.checks.forEach(check => {
        const card = document.createElement('div');
        card.className = 'card check-card';
        card.dataset.checkName = check.name;

        const badgeClass = STATUS_BADGE[check.status] || 'badge-blue';
        const label = CHECK_LABELS[check.name] || check.name;

        card.innerHTML = `
            <div class="card-header flex items-center justify-between cursor-pointer" onclick="toggleCheckDetail(this)">
                <span>${label}</span>
                <span class="badge ${badgeClass}">${check.status.toUpperCase()}</span>
            </div>
            <div class="check-detail open">
                <div class="card-body">${renderCheckDetails(check)}</div>
            </div>
        `;
        container.appendChild(card);
    });

    filterValidationChecks();
}

function renderCheckDetails(check) {
    const d = check.details;
    switch (check.name) {
        case 'schema_completeness':
            return `<div class="grid grid-cols-3 gap-4 text-center">
                <div><div class="text-xl font-bold">${d.owl_classes}</div><div class="stat-label">OWL Classes</div></div>
                <div><div class="text-xl font-bold">${d.data_properties}</div><div class="stat-label">Data Props</div></div>
                <div><div class="text-xl font-bold">${d.object_properties}</div><div class="stat-label">Object Props</div></div>
            </div>`;

        case 'spatial_hierarchy':
            return `<div class="grid grid-cols-2 gap-4 text-center">
                <div><div class="text-xl font-bold">${d.complete_chains}</div><div class="stat-label">Complete Chains</div></div>
                <div><div class="text-xl font-bold">${d.storeys}</div><div class="stat-label">Storeys</div></div>
            </div>
            <p class="text-xs text-gray-500 mt-2">Project → Site → Building → Storey</p>`;

        case 'element_statistics': {
            const top5 = (d.categories || []).slice(0, 5);
            let rows = top5.map(c => `<tr><td class="text-sm">${c.name}</td><td class="text-sm text-right">${formatNumber(c.count)}</td></tr>`).join('');
            return `<div class="text-center mb-3"><div class="text-xl font-bold">${formatNumber(d.total_elements)}</div><div class="stat-label">${d.category_count} Categories</div></div>
                <table><thead><tr><th>Category</th><th class="text-right">Count</th></tr></thead><tbody>${rows}</tbody></table>`;
        }

        case 'uri_consistency':
            return `<div class="grid grid-cols-2 gap-4 text-center">
                <div><div class="text-xl font-bold ${d.orphan_elements > 0 ? 'text-red-400' : ''}">${d.orphan_elements}</div><div class="stat-label">Orphan Elements</div></div>
                <div><div class="text-xl font-bold ${d.unlinked_elements > 0 ? 'text-yellow-400' : ''}">${d.unlinked_elements}</div><div class="stat-label">Unlinked Elements</div></div>
            </div>`;

        case 'property_set_coverage': {
            const pct = Math.round(d.coverage_ratio * 100);
            const barColor = pct >= 30 ? '#4ade80' : (pct > 0 ? '#fbbf24' : '#f87171');
            return `<div class="grid grid-cols-3 gap-4 text-center mb-3">
                <div><div class="text-xl font-bold">${d.total_property_sets}</div><div class="stat-label">PropertySets</div></div>
                <div><div class="text-xl font-bold">${d.plant_property_sets}</div><div class="stat-label">Plant PSets</div></div>
                <div><div class="text-xl font-bold">${d.elements_with_pset}/${d.total_elements}</div><div class="stat-label">With PSet</div></div>
            </div>
            <div class="progress-bar"><div class="progress-fill" style="width:${pct}%;background:${barColor}"></div></div>
            <p class="text-xs text-gray-500 mt-1">Coverage: ${pct}%</p>`;
        }

        case 'required_properties':
            return `<div class="text-center">
                <div class="text-xl font-bold ${d.missing_global_id > 0 ? 'text-red-400' : 'text-green-400'}">${d.missing_global_id}</div>
                <div class="stat-label">Missing GlobalId</div>
            </div>`;

        case 'classification_quality': {
            const otherPct = Math.round(d.other_ratio * 100);
            const threshold = 15;
            return `<div class="grid grid-cols-2 gap-4 text-center mb-2">
                <div><div class="text-xl font-bold">${d.other_count}</div><div class="stat-label">"Other" Count</div></div>
                <div><div class="text-xl font-bold">${d.total_categorized}</div><div class="stat-label">Total Categorized</div></div>
            </div>
            <p class="text-xs ${otherPct > threshold ? 'text-yellow-400' : 'text-gray-500'}">Other ratio: ${otherPct}% (threshold: ${threshold}%)</p>`;
        }

        case 'relationship_integrity':
            return `<div class="grid grid-cols-3 gap-4 text-center">
                <div><div class="text-xl font-bold">${d.contains_element}</div><div class="stat-label">containsElement</div></div>
                <div><div class="text-xl font-bold">${d.is_contained_in}</div><div class="stat-label">isContainedIn</div></div>
                <div><div class="text-xl font-bold ${d.asymmetric_pairs > 0 ? 'text-yellow-400' : 'text-green-400'}">${d.asymmetric_pairs}</div><div class="stat-label">Asymmetric</div></div>
            </div>
            <p class="text-xs mt-2 ${d.symmetric ? 'text-green-400' : 'text-yellow-400'}">Symmetric: ${d.symmetric ? 'Yes' : 'No'}</p>`;

        default:
            return `<pre class="text-xs text-gray-400">${JSON.stringify(d, null, 2)}</pre>`;
    }
}

function toggleCheckDetail(header) {
    const detail = header.nextElementSibling;
    detail.classList.toggle('open');
}

function filterValidationChecks() {
    const checks = document.querySelectorAll('#val-filters input[data-check]');
    const visible = new Set();
    checks.forEach(cb => { if (cb.checked) visible.add(cb.dataset.check); });

    document.querySelectorAll('.check-card').forEach(card => {
        card.classList.toggle('hidden', !visible.has(card.dataset.checkName));
    });
}

// ── Other Category Explorer ──

let otherPage = 0;
const OTHER_PAGE_SIZE = 50;

function suggestCategory(name) {
    if (/degree direction change|weldolet|sockolet|eccentric.*size|concentric.*size|nipple|^90e-|^45.*degree/i.test(name)) return 'PipeFitting';
    if (/^anvil_|^hgr|^assy_|hex.?nut/i.test(name)) return 'Hanger';
    if (/^[a-z][0-9]?$/i.test(name) || /^n[0-9]+$/i.test(name)) return 'Nozzle';
    if (/distillation|recovery unit/i.test(name)) return 'Equipment';
    if (/^[a-z]-\d{3}$/i.test(name)) return 'Equipment';
    if (/^suction$|^discharge$/i.test(name)) return 'Pump';
    if (/ladder|manhole|pullpit|safety/i.test(name)) return 'Access';
    if (/^vg3-|^stnoz|^vc[0-9]|^vl[0-9]/i.test(name)) return 'Valve';
    if (/^pr01-|^b0n-/i.test(name)) return 'SystemRef';
    return null;
}

const SUGGEST_COLORS = {
    PipeFitting: '#3b82f6', Hanger: '#f59e0b', Nozzle: '#8b5cf6',
    Equipment: '#10b981', Pump: '#06b6d4', Access: '#ec4899',
    Valve: '#ef4444', SystemRef: '#64748b',
};

async function loadOtherElements() {
    const file = document.getElementById('val-ttl-select').value;
    const pattern = document.getElementById('other-name-filter').value.trim();
    const tbody = document.getElementById('other-elements-table');
    tbody.innerHTML = '<tr><td colspan="5" class="loading"><div class="spinner"></div>Loading other elements...</td></tr>';

    let url = '/api/reasoning/other-elements?limit=' + OTHER_PAGE_SIZE + '&offset=' + (otherPage * OTHER_PAGE_SIZE);
    if (file) url += '&ttl_file=' + encodeURIComponent(file);
    if (pattern) url += '&name_pattern=' + encodeURIComponent(pattern);

    const data = await api(url);
    if (!data) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-red-400">Failed to load.</td></tr>';
        return;
    }

    renderOtherGroups(data.name_groups || []);

    if (data.elements.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-gray-500">No elements found. Try adjusting the name filter.</td></tr>';
    } else {
        tbody.innerHTML = data.elements.map(function(e) {
            var sug = suggestCategory(e.name);
            var sugBadge = sug
                ? '<span class="badge" style="background:' + (SUGGEST_COLORS[sug] || '#334155') + '22;color:' + (SUGGEST_COLORS[sug] || '#94a3b8') + '">' + sug + '</span>'
                : '<span class="text-gray-600">-</span>';
            return '<tr>' +
                '<td>' + (e.name || '-') + '</td>' +
                '<td class="text-gray-400 text-xs">' + (e.original_type || '-') + '</td>' +
                '<td>' + (e.storey || '<span class="text-gray-600">-</span>') + '</td>' +
                '<td class="text-gray-500 text-xs font-mono">' + (e.global_id || '-') + '</td>' +
                '<td>' + sugBadge + '</td>' +
                '</tr>';
        }).join('');
    }

    document.getElementById('other-info').textContent =
        'Showing ' + (data.offset + 1) + '-' + Math.min(data.offset + data.elements.length, data.total) + ' of ' + data.total + ' "Other" elements (page ' + (otherPage + 1) + ')';
}

function renderOtherGroups(groups) {
    var container = document.getElementById('other-groups');
    if (groups.length === 0) { container.innerHTML = ''; return; }
    container.innerHTML = groups.map(function(g) {
        var color = SUGGEST_COLORS[g.suggested_category] || '#94a3b8';
        return '<div class="card cursor-pointer" style="border-left:3px solid ' + color + '" onclick="filterOtherByGroup(\'' + (g.examples[0] || '').replace(/'/g, "\\'") + '\')">' +
            '<div class="card-body" style="padding:12px">' +
                '<div class="flex items-center justify-between mb-1">' +
                    '<span class="text-sm font-semibold">' + g.pattern + '</span>' +
                    '<span class="badge" style="background:' + color + '22;color:' + color + '">' + g.suggested_category + '</span>' +
                '</div>' +
                '<div class="text-lg font-bold">' + g.count + '</div>' +
                '<div class="text-xs text-gray-500 mt-1">' + g.examples.slice(0, 2).join(', ') + '</div>' +
            '</div>' +
        '</div>';
    }).join('');
}

function filterOtherByGroup(example) {
    var input = document.getElementById('other-name-filter');
    var prefix = example.replace(/-\d+$/, '').trim();
    input.value = prefix;
    otherPage = 0;
    loadOtherElements();
}

function otherNextPage() { otherPage++; loadOtherElements(); }
function otherPrevPage() { if (otherPage > 0) { otherPage--; loadOtherElements(); } }

// ── Node Explorer Tab ──

const PREFIX_MAP = {
    'http://example.org/bim-ontology/schema#': 'bim:',
    'http://example.org/bim-ontology/instance#': 'inst:',
    'http://www.w3.org/2002/07/owl#': 'owl:',
    'http://www.w3.org/2000/01/rdf-schema#': 'rdfs:',
    'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf:',
    'https://standards.buildingsmart.org/IFC/DEV/IFC4/ADD2/OWL#': 'ifc:',
    'http://www.w3.org/2001/XMLSchema#': 'xsd:',
};

function shortenUri(uri) {
    if (!uri) return '';
    for (const [long, short] of Object.entries(PREFIX_MAP)) {
        if (uri.startsWith(long)) return short + uri.slice(long.length);
    }
    return uri;
}

let explorerInited = false;
let expSelectedType = null;  // null = All
let expPage = 0;
const EXP_PAGE_SIZE = 50;

async function initExplorer() {
    if (explorerInited) return;
    explorerInited = true;

    // Load TTL file list for explorer
    const fileData = await api('/api/reasoning/ttl-files');
    if (fileData) {
        const select = document.getElementById('exp-ttl-select');
        select.innerHTML = '';
        fileData.files.forEach(f => {
            const opt = document.createElement('option');
            opt.value = f.name;
            opt.textContent = `${f.name} (${f.size_kb} KB)`;
            if (f.name === fileData.current) opt.selected = true;
            select.appendChild(opt);
        });
    }

    await Promise.all([loadNodeTypes(), loadNodePredicates()]);
}

function refreshExplorer() {
    explorerInited = false;
    expSelectedType = null;
    expPage = 0;
    initExplorer();
}

async function loadNodeTypes() {
    const container = document.getElementById('exp-types');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading node types...</div>';

    const file = document.getElementById('exp-ttl-select').value;
    let url = '/api/reasoning/node-types';
    if (file) url += '?ttl_file=' + encodeURIComponent(file);

    const data = await api(url);
    if (!data || !data.types) {
        container.innerHTML = '<p class="text-gray-500 text-sm">Failed to load types.</p>';
        return;
    }

    // Calculate total count
    const totalCount = data.types.reduce((sum, t) => sum + t.count, 0);

    let html = '';
    // "All" option
    html += `<div class="type-radio ${expSelectedType === null ? 'selected' : ''}" data-type="" onclick="selectNodeType(null, this)">
        <span>All</span>
        <span class="badge badge-blue">${formatNumber(totalCount)}</span>
    </div>`;

    data.types.forEach(t => {
        const isSelected = expSelectedType === t.short;
        html += `<div class="type-radio ${isSelected ? 'selected' : ''}" data-type="${t.short}" onclick="selectNodeType('${t.short}', this)">
            <span class="truncate" title="${t.uri}">${t.short}</span>
            <span class="badge badge-blue">${formatNumber(t.count)}</span>
        </div>`;
    });

    container.innerHTML = html;
}

function selectNodeType(typeShort, el) {
    expSelectedType = typeShort;
    expPage = 0;
    // Update radio visual
    document.querySelectorAll('#exp-types .type-radio').forEach(r => r.classList.remove('selected'));
    if (el) el.classList.add('selected');
    loadNodes();
}

async function loadNodePredicates() {
    const container = document.getElementById('exp-columns');
    const file = document.getElementById('exp-ttl-select').value;
    let url = '/api/reasoning/node-predicates';
    if (file) url += '?ttl_file=' + encodeURIComponent(file);

    const data = await api(url);
    if (!data || !data.predicates) {
        container.innerHTML = '<span class="text-gray-500 text-xs">No predicates found. Try refreshing or selecting another TTL file.</span>';
        return;
    }

    // Default checked predicates
    const defaultChecked = new Set(['bim:hasName', 'bim:hasCategory', 'bim:hasGlobalId', 'bim:hasOriginalType']);

    container.innerHTML = data.predicates.map(p => {
        const checked = defaultChecked.has(p.short) ? 'checked' : '';
        return `<label class="col-check" title="${p.uri} (${p.count})">
            <input type="checkbox" value="${p.short}" ${checked}>
            <span>${p.short}</span>
            <span class="text-gray-600">(${formatNumber(p.count)})</span>
        </label>`;
    }).join('');
}

function getSelectedColumns() {
    const checks = document.querySelectorAll('#exp-columns input[type=checkbox]:checked');
    return Array.from(checks).map(cb => cb.value);
}

async function loadNodes() {
    const tbody = document.getElementById('exp-tbody');
    const thead = document.getElementById('exp-thead');
    const info = document.getElementById('exp-info');
    const pageInfo = document.getElementById('exp-page-info');

    const columns = getSelectedColumns();
    if (columns.length === 0) {
        tbody.innerHTML = '<tr><td class="text-gray-500">Select at least one predicate column (tip: start with bim:hasName, bim:hasCategory).</td></tr>';
        thead.innerHTML = '<tr><th>subject</th></tr>';
        info.textContent = '--';
        pageInfo.textContent = '';
        return;
    }

    tbody.innerHTML = '<tr><td colspan="' + (columns.length + 1) + '" class="loading"><div class="spinner"></div>Loading nodes...</td></tr>';

    const file = document.getElementById('exp-ttl-select').value;
    const search = document.getElementById('exp-search').value.trim();

    let url = '/api/reasoning/nodes?limit=' + EXP_PAGE_SIZE + '&offset=' + (expPage * EXP_PAGE_SIZE);
    if (file) url += '&ttl_file=' + encodeURIComponent(file);
    if (expSelectedType) url += '&type_filter=' + encodeURIComponent(expSelectedType);
    url += '&columns=' + encodeURIComponent(columns.join(','));
    if (search) url += '&search=' + encodeURIComponent(search);

    const data = await api(url);
    if (!data) {
        tbody.innerHTML = '<tr><td colspan="' + (columns.length + 1) + '" class="text-red-400">Failed to load nodes.</td></tr>';
        return;
    }

    // Render header
    thead.innerHTML = '<tr><th>subject</th>' + columns.map(c => `<th>${c}</th>`).join('') + '</tr>';

    if (data.rows.length === 0) {
        tbody.innerHTML = '<tr><td colspan="' + (columns.length + 1) + '" class="text-center text-gray-500">No nodes found. Try clearing filters or selecting a different type.</td></tr>';
        info.textContent = '0 total';
        pageInfo.textContent = '';
        return;
    }

    tbody.innerHTML = data.rows.map(row => {
        const subjDisplay = row.subject.length > 50 ? row.subject.slice(0, 50) + '...' : row.subject;
        let cells = `<td class="cursor-pointer text-blue-400 hover:underline" title="${row.subject_uri}" onclick="showNodeDetail('${row.subject.replace(/'/g, "\\'")}')">
            <span class="font-mono text-xs">${subjDisplay}</span>
        </td>`;
        row.values.forEach(v => {
            const display = v.length > 40 ? v.slice(0, 40) + '...' : v;
            cells += `<td class="text-sm" title="${v}">${display || '<span class="text-gray-600">-</span>'}</td>`;
        });
        return '<tr>' + cells + '</tr>';
    }).join('');

    const totalPages = Math.ceil(data.total / EXP_PAGE_SIZE);
    info.textContent = formatNumber(data.total) + ' total';
    pageInfo.textContent = 'Page ' + (expPage + 1) + ' of ' + (totalPages || 1);
}

function expNextPage() { expPage++; loadNodes(); }
function expPrevPage() { if (expPage > 0) { expPage--; loadNodes(); } }

async function showNodeDetail(subjectShort) {
    const detailDiv = document.getElementById('exp-detail');
    const titleEl = document.getElementById('exp-detail-title');
    const bodyEl = document.getElementById('exp-detail-body');

    detailDiv.style.display = 'block';
    titleEl.textContent = subjectShort;
    bodyEl.innerHTML = '<div class="loading"><div class="spinner"></div>Loading triples...</div>';

    const file = document.getElementById('exp-ttl-select').value;
    let url = '/api/reasoning/node-detail?subject=' + encodeURIComponent(subjectShort);
    if (file) url += '&ttl_file=' + encodeURIComponent(file);

    const data = await api(url);
    if (!data || !data.triples) {
        bodyEl.innerHTML = '<p class="text-red-400 text-sm">Failed to load node detail.</p>';
        return;
    }

    if (data.triples.length === 0) {
        bodyEl.innerHTML = '<p class="text-gray-500 text-sm">No triples found for this subject.</p>';
        return;
    }

    let html = '<table><thead><tr><th>predicate</th><th>object</th></tr></thead><tbody>';
    data.triples.forEach(t => {
        html += `<tr>
            <td class="text-blue-400 text-xs font-mono">${t.predicate}</td>
            <td class="text-sm" title="${t.object}">${t.object}</td>
        </tr>`;
    });
    html += '</tbody></table>';
    html += `<p class="text-xs text-gray-500 mt-2">${data.triples.length} triples</p>`;
    bodyEl.innerHTML = html;

    // Scroll to detail
    detailDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function toggleExpDetail() {
    const body = document.getElementById('exp-detail-body');
    body.style.display = body.style.display === 'none' ? 'block' : 'none';
}

// ── Lean Layer Tab ──

async function loadLeanStats() {
    const data = await api('/api/lean/stats');
    if (!data) return;
    document.getElementById('lean-tasks').textContent = formatNumber(data.tasks);
    document.getElementById('lean-iwps').textContent = formatNumber(data.iwps);
    document.getElementById('lean-statuses').textContent = formatNumber(data.statuses);
    document.getElementById('lean-equipment').textContent = formatNumber(data.equipment);

    const summary = document.getElementById('lean-summary');
    summary.innerHTML = `
        <table><tbody>
            <tr><td class="text-gray-400">Construction Tasks</td><td class="text-right">${formatNumber(data.tasks)}</td></tr>
            <tr><td class="text-gray-400">Work Areas (CWA)</td><td class="text-right">${formatNumber(data.cwas)}</td></tr>
            <tr><td class="text-gray-400">Work Packages (CWP)</td><td class="text-right">${formatNumber(data.cwps)}</td></tr>
            <tr><td class="text-gray-400">Installation WPs (IWP)</td><td class="text-right">${formatNumber(data.iwps)}</td></tr>
            <tr><td class="text-gray-400">Element Statuses</td><td class="text-right">${formatNumber(data.statuses)}</td></tr>
            <tr><td class="text-gray-400">Equipment</td><td class="text-right">${formatNumber(data.equipment)}</td></tr>
            <tr><td class="text-gray-400">With Delivery Status</td><td class="text-right">${formatNumber(data.with_delivery)}</td></tr>
            <tr><td class="text-gray-400">Assigned to IWP</td><td class="text-right">${formatNumber(data.with_iwp)}</td></tr>
            <tr><td class="text-gray-400">Elements with Unit Cost</td><td class="text-right">${formatNumber(data.with_unit_cost)}</td></tr>
            <tr><td class="text-gray-400">Elements with Consume Duration</td><td class="text-right">${formatNumber(data.with_consume_duration)}</td></tr>
            <tr><td class="text-gray-400">Tasks with Cost</td><td class="text-right">${formatNumber(data.tasks_with_cost)}</td></tr>
            <tr><td class="text-gray-400">Tasks with Typed Duration</td><td class="text-right">${formatNumber(data.tasks_with_typed_duration)}</td></tr>
            <tr><td class="text-gray-400">Tasks with Legacy Duration</td><td class="text-right">${formatNumber(data.tasks_with_legacy_duration)}</td></tr>
            <tr><td class="text-gray-400">Total Unit Cost</td><td class="text-right">${formatDecimal(data.total_unit_cost)}</td></tr>
            <tr><td class="text-gray-400">Avg Unit Cost</td><td class="text-right">${formatDecimal(data.avg_unit_cost)}</td></tr>
            <tr><td class="text-gray-400">Avg Consume Duration (days)</td><td class="text-right">${formatDecimal(data.avg_consume_duration)}</td></tr>
            <tr><td class="text-gray-400">Avg Effective Task Duration (days)</td><td class="text-right">${formatDecimal(data.avg_task_duration_effective)}</td></tr>
        </tbody></table>
    `;
}

async function injectLeanCSV() {
    const type = document.getElementById('lean-inject-type').value;
    const fileInput = document.getElementById('lean-csv-file');
    const result = document.getElementById('lean-inject-result');

    if (!fileInput.files || fileInput.files.length === 0) {
        result.innerHTML = '<span class="text-red-400">Please select a CSV file.</span>';
        return;
    }

    result.innerHTML = '<div class="loading"><div class="spinner"></div>Injecting...</div>';

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const res = await fetch(`/api/lean/inject/${type}`, { method: 'POST', body: formData });
        const data = await res.json();
        if (res.ok) {
            result.innerHTML = `<span class="text-green-400">Success!</span><pre class="text-xs text-gray-400 mt-1">${JSON.stringify(data, null, 2)}</pre>`;
            loadLeanStats();
            checkHealth();
        } else {
            result.innerHTML = `<span class="text-red-400">Error: ${data.detail || 'Unknown error'}</span>`;
        }
    } catch (e) {
        result.innerHTML = `<span class="text-red-400">Error: ${e.message}</span>`;
    }
}

// ── Today's Work Tab ──

function initTodaysWork() {
    const dateInput = document.getElementById('tw-date');
    if (!dateInput.value) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }
}

async function loadTodaysWork() {
    const targetDate = document.getElementById('tw-date').value;
    if (!targetDate) return;

    const container = document.getElementById('tw-table');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading work packages...</div>';

    const data = await api(`/api/lean/today?target_date=${targetDate}`);
    if (!data) {
        container.innerHTML = '<p class="text-red-400">Failed to load.</p>';
        return;
    }

    document.getElementById('tw-summary').style.display = 'grid';
    document.getElementById('tw-iwp-count').textContent = data.iwp_count;
    const totalElems = data.work_packages.reduce((s, w) => s + w.element_count, 0);
    document.getElementById('tw-elem-count').textContent = totalElems;
    const execCount = data.work_packages.filter(w => w.is_executable === 'true').length;
    document.getElementById('tw-exec-count').textContent = execCount;
    document.getElementById('tw-info').textContent = `Date: ${data.target_date}`;

    if (data.work_packages.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-sm">No active work packages for this date.</p>';
        return;
    }

    const statusColors = {
        AllCleared: '#4ade80', PendingMaterial: '#fbbf24',
        PendingApproval: '#f97316', PendingPredecessor: '#f87171',
    };

    let html = '<table><thead><tr><th>IWP</th><th>CWP</th><th>CWA</th><th>Period</th><th>Elements</th><th>Constraint</th></tr></thead><tbody>';
    data.work_packages.forEach(w => {
        const color = statusColors[w.constraint_status] || '#94a3b8';
        html += `<tr>
            <td><span class="badge badge-blue">${w.iwp}</span></td>
            <td class="text-sm">${w.cwp}</td>
            <td class="text-sm">${w.cwa}</td>
            <td class="text-xs text-gray-400">${w.start_date} ~ ${w.end_date}</td>
            <td class="text-center">${w.element_count}</td>
            <td><span class="badge" style="background:${color}22;color:${color}">${w.constraint_status || '-'}</span></td>
        </tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}

// ── Status Monitor Tab ──

let deliveryChart = null;

function initStatusMonitor() {
    const dateInput = document.getElementById('sm-ref-date');
    if (!dateInput.value) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }
    loadDeliveryStatusChart();
}

async function loadDelayed() {
    const refDate = document.getElementById('sm-ref-date').value;
    const list = document.getElementById('sm-delayed-list');
    list.innerHTML = '<div class="loading"><div class="spinner"></div>Loading delayed elements...</div>';

    const data = await api(`/api/lean/delayed?reference_date=${refDate}`);
    if (!data) {
        list.innerHTML = '<p class="text-red-400">Failed to load.</p>';
        return;
    }

    document.getElementById('sm-delayed-count').textContent = data.delayed_count;

    if (data.elements.length === 0) {
        list.innerHTML = '<p class="text-green-400 text-sm">No delayed elements found.</p>';
        return;
    }

    let html = '<table><thead><tr><th>Name</th><th>Category</th><th>Planned</th><th>Status</th></tr></thead><tbody>';
    data.elements.forEach(e => {
        html += `<tr>
            <td class="text-sm">${e.name}</td>
            <td><span class="badge badge-blue">${e.category}</span></td>
            <td class="text-xs text-gray-400">${e.planned_date}</td>
            <td><span class="badge badge-red">${e.delivery_status}</span></td>
        </tr>`;
    });
    html += '</tbody></table>';
    list.innerHTML = html;
}

async function loadDeliveryStatusChart() {
    const data = await api('/api/lean/stats');
    if (!data || data.with_delivery === 0) {
        document.getElementById('sm-status-table').innerHTML = '<p class="text-gray-500 text-sm">No delivery status data available. Inject schedule/status CSV first.</p>';
        return;
    }

    // Query delivery status distribution via SPARQL
    const sparqlData = await apiPost('/api/sparql', {
        query: `PREFIX bim: <http://example.org/bim-ontology/schema#>
SELECT ?status (COUNT(?e) AS ?count) WHERE {
    ?e bim:hasDeliveryStatus ?status .
} GROUP BY ?status ORDER BY DESC(?count)`
    });

    if (!sparqlData || !sparqlData.results || sparqlData.results.length === 0) {
        document.getElementById('sm-status-table').innerHTML = '<p class="text-gray-500 text-sm">No status data.</p>';
        return;
    }

    const statusColors = {
        Ordered: '#64748b', InProduction: '#3b82f6', Shipped: '#f59e0b',
        OnSite: '#10b981', Installed: '#4ade80', Inspected: '#8b5cf6',
        Delayed: '#ef4444', Planned: '#94a3b8',
    };

    const labels = sparqlData.results.map(r => r.status);
    const counts = sparqlData.results.map(r => parseInt(r.count));
    const colors = labels.map(l => statusColors[l] || '#64748b');

    const ctx = document.getElementById('chart-delivery-status').getContext('2d');
    if (deliveryChart) deliveryChart.destroy();
    deliveryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{ data: counts, backgroundColor: colors, borderWidth: 0 }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'right', labels: { color: '#94a3b8', font: { size: 11 } } } }
        }
    });

    let html = '<table><thead><tr><th>Status</th><th class="text-right">Count</th></tr></thead><tbody>';
    sparqlData.results.forEach(r => {
        const color = statusColors[r.status] || '#94a3b8';
        html += `<tr><td><span class="badge" style="background:${color}22;color:${color}">${r.status}</span></td><td class="text-right">${r.count}</td></tr>`;
    });
    html += '</tbody></table>';
    document.getElementById('sm-status-table').innerHTML = html;
}

async function updateElementStatus() {
    const gid = document.getElementById('sm-update-gid').value.trim();
    const statusValue = document.getElementById('sm-update-status').value;
    const deliveryStatus = document.getElementById('sm-update-delivery').value;
    const result = document.getElementById('sm-update-result');

    if (!gid) {
        result.innerHTML = '<span class="text-red-400">Please enter a GlobalId.</span>';
        return;
    }

    const data = await api(`/api/lean/status/${encodeURIComponent(gid)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status_value: statusValue, delivery_status: deliveryStatus }),
    });

    if (data && data.success) {
        result.innerHTML = `<span class="text-green-400">Updated: ${gid} -> ${statusValue}</span>`;
        loadDeliveryStatusChart();
    } else {
        result.innerHTML = `<span class="text-red-400">Error: ${data?.detail || data?.error || 'Unknown'}</span>`;
    }
}

// ── Hierarchy Tab ──

let hierarchyFilesLoaded = false;
let hierarchyDrillData = null;
const HIERARCHY_DEFAULT_DETAIL_HTML = '<p class="text-gray-500 text-sm">Select a node from either tree to view contained elements and level distribution.</p>';

function resetHierarchyDetails() {
    const container = document.getElementById('hierarchy-details');
    if (container) container.innerHTML = HIERARCHY_DEFAULT_DETAIL_HTML;
}

function buildHierarchyDrillData(rows, maxDepth) {
    const nodesByPath = new Map();
    const childrenByPath = new Map();
    const roots = [];
    const typeColors = {
        'Project': '#8b5cf6',
        'Area': '#3b82f6',
        'Unit': '#10b981',
        'System': '#64748b'
    };

    rows.forEach(row => {
        const path = row.path;
        const parts = path.split('\\\\');
        if (parts.length > maxDepth) return;
        const depth = parts.length;
        const typeName = row.type.split('#').pop();
        nodesByPath.set(path, {
            path,
            name: row.name,
            type: typeName,
            children: parseInt(row.children) || 0,
            color: typeColors[typeName] || '#94a3b8',
            depth,
        });
    });

    nodesByPath.forEach(node => {
        const parts = node.path.split('\\\\');
        const parentPath = parts.slice(0, -1).join('\\\\');
        if (parentPath && nodesByPath.has(parentPath)) {
            if (!childrenByPath.has(parentPath)) childrenByPath.set(parentPath, []);
            childrenByPath.get(parentPath).push(node);
        } else {
            roots.push(node);
        }
    });

    const sortNodes = (list) => {
        list.sort((a, b) => {
            if (b.children !== a.children) return b.children - a.children;
            return a.name.localeCompare(b.name);
        });
    };

    sortNodes(roots);
    childrenByPath.forEach(sortNodes);

    return { nodesByPath, childrenByPath, roots, maxDepth };
}

function renderSystemPathTree() {
    const container = document.getElementById('hierarchy-tree-view');
    if (!container) return;
    container.innerHTML = '';

    if (!hierarchyDrillData || hierarchyDrillData.roots.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-sm">No system path nodes found. Try increasing depth or loading a different file.</p>';
        return;
    }

    function createNodeEl(node) {
        const div = document.createElement('div');
        div.className = 'hierarchy-node';

        const header = document.createElement('div');
        header.className = 'tree-item flex items-center gap-2';

        const children = hierarchyDrillData.childrenByPath.get(node.path) || [];
        const hasChildren = children.length > 0;

        const arrow = document.createElement('span');
        arrow.className = 'text-xs';
        arrow.style.color = '#64748b';
        arrow.style.width = '14px';
        arrow.style.display = 'inline-block';
        arrow.style.textAlign = 'center';
        arrow.textContent = hasChildren ? '\u25B6' : '\u2022';

        const icon = document.createElement('span');
        icon.className = 'node-icon';
        icon.style.background = node.color;

        const name = document.createElement('span');
        name.className = 'text-sm';
        name.style.flex = '1';
        name.textContent = node.name || 'Unnamed';

        const badge = document.createElement('span');
        badge.className = 'badge';
        badge.style.background = `${node.color}22`;
        badge.style.color = node.color;
        badge.textContent = node.type;

        const count = document.createElement('span');
        count.className = 'text-xs text-gray-500';
        count.textContent = node.children > 0 ? `(${node.children})` : '';

        header.appendChild(arrow);
        header.appendChild(icon);
        header.appendChild(name);
        header.appendChild(badge);
        if (count.textContent) header.appendChild(count);

        div.appendChild(header);

        if (hasChildren) {
            const childContainer = document.createElement('div');
            childContainer.className = 'children';
            childContainer.style.display = 'none';

            children.forEach(child => childContainer.appendChild(createNodeEl(child)));
            div.appendChild(childContainer);

            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                const isOpen = childContainer.style.display !== 'none';
                childContainer.style.display = isOpen ? 'none' : 'block';
                arrow.textContent = isOpen ? '\u25B6' : '\u25BC';
                loadHierarchyNodeDetail(node.path, node.name);
            });
        } else {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => loadHierarchyNodeDetail(node.path, node.name));
        }

        return div;
    }

    hierarchyDrillData.roots.forEach(root => container.appendChild(createNodeEl(root)));
}

async function loadHierarchyFiles() {
    if (hierarchyFilesLoaded) return;

    const select = document.getElementById('hierarchy-file-select');
    const data = await api('/api/reasoning/ttl-files');

    if (!data || !data.files) {
        select.innerHTML = '<option value="">Failed to load files</option>';
        return;
    }

    select.innerHTML = data.files
        .filter(f => f.name.endsWith('.ttl') || f.name.endsWith('.ttl.bak'))
        .map(f => {
            const label = f.name.endsWith('.bak') ? `${f.name} [IFC backup]` : f.name;
            const selected = f.name === 'nwd4op-12.ttl' ? 'selected' : '';
            return `<option value="${f.name}" ${selected}>${label} (${f.size_kb} KB)</option>`;
        })
        .join('');

    hierarchyFilesLoaded = true;
}

async function loadSelectedFile() {
    const select = document.getElementById('hierarchy-file-select');
    const status = document.getElementById('hierarchy-file-status');
    const fileName = select.value;

    if (!fileName) {
        status.textContent = 'Please select a file';
        status.style.color = '#f87171';
        return;
    }

    status.textContent = 'Loading graph...';
    status.style.color = '#94a3b8';

    try {
        const data = await apiPost(`/api/reasoning/reload?file_name=${encodeURIComponent(fileName)}`, {});

        if (data && data.status === 'success') {
            status.textContent = `Loaded: ${formatNumber(data.triples)} triples`;
            status.style.color = '#4ade80';

            // Refresh all data
            checkHealth();
            loadMaxLevel();
            loadHierarchyComparison();
            resetHierarchyDetails();
            loadHierarchyTree();
            loadNavisHierarchyTree();
        } else {
            status.textContent = `Error: ${data?.detail || 'Unknown'}`;
            status.style.color = '#f87171';
        }
    } catch (e) {
        status.textContent = `Error: ${e.message}`;
        status.style.color = '#f87171';
    }
}

async function loadHierarchyComparison() {
    const container = document.getElementById('hierarchy-comparison');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading hierarchy summary...</div>';

    // Optimized query - simple type count
    const statsQuery = `
PREFIX navis: <http://example.org/bim-ontology/navis#>

SELECT ?type (COUNT(?s) AS ?count)
WHERE {
    ?s a ?type .
    FILTER(?type IN (navis:Project, navis:Area, navis:Unit, navis:System, navis:SP3DEntity))
}
GROUP BY ?type`;

    const data = await apiPost('/api/sparql', { query: statsQuery });

    if (!data || !data.results || data.results.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-sm">No hierarchy stats found. Load a TTL file with Navis metadata.</p>';
        return;
    }

    // Parse type counts from results
    const stats = { projects: 0, areas: 0, units: 0, systems: 0, elements: 0 };
    data.results.forEach(row => {
        const typeName = (row.type || '').split('#').pop();
        const count = parseInt(row.count) || 0;
        if (typeName === 'Project') stats.projects = count;
        else if (typeName === 'Area') stats.areas = count;
        else if (typeName === 'Unit') stats.units = count;
        else if (typeName === 'System') stats.systems = count;
        else if (typeName === 'SP3DEntity') stats.elements = count;
    });

    const maxLevelText = metadataCache.maxLevel && metadataCache.maxLevel > 0 ? metadataCache.maxLevel : '--';
    const propValuesText = metadataCache.totalProps == null ? '--' : formatNumber(metadataCache.totalProps);

    container.innerHTML = `
        <div class="flex flex-wrap gap-2 mb-3">
            <span class="badge badge-blue" id="hierarchy-max-level">Max Level: ${maxLevelText}</span>
            <span class="badge badge-green" id="hierarchy-prop-count">Property Values: ${propValuesText}</span>
        </div>
        <div class="mb-4">
            <h4 class="text-sm font-semibold text-blue-400 mb-2">Current Data (dxtnavis)</h4>
            <table>
                <tbody>
                    <tr><td class="text-gray-400">Projects</td><td class="text-right font-bold">${stats.projects}</td></tr>
                    <tr><td class="text-gray-400">Areas</td><td class="text-right font-bold">${stats.areas}</td></tr>
                    <tr><td class="text-gray-400">Units</td><td class="text-right font-bold">${stats.units}</td></tr>
                    <tr><td class="text-gray-400">Systems</td><td class="text-right font-bold">${stats.systems}</td></tr>
                    <tr><td class="text-gray-400">Elements</td><td class="text-right font-bold text-green-400">${stats.elements}</td></tr>
                </tbody>
            </table>
        </div>
        <div class="p-3 rounded" style="background:#1e3a5f22; border: 1px solid #1e3a5f;">
            <h4 class="text-xs font-semibold text-blue-400 mb-2">vs IFC Export</h4>
            <div class="text-xs text-gray-400">
                <div>IFC: 1 Project → 1 Storey → 3,911 elem</div>
                <div class="text-green-400 mt-1">+${(parseInt(stats.elements) - 3911).toLocaleString()} elements</div>
                <div class="text-green-400">+${(parseInt(stats.projects) + parseInt(stats.areas) + parseInt(stats.units) + parseInt(stats.systems) - 4).toLocaleString()} hierarchy nodes</div>
            </div>
        </div>
    `;
}

async function loadLevelDistribution() {
    const container = document.getElementById('level-distribution');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading level distribution...</div>';

    // Query level distribution from original CSV Level (navis:hasLevel)
    const query = `
PREFIX navis: <http://example.org/bim-ontology/navis#>

SELECT ?level (COUNT(?elem) AS ?count)
WHERE {
    ?elem a navis:SP3DEntity ;
          navis:hasLevel ?level .
}
GROUP BY ?level
ORDER BY ?level`;

    const data = await apiPost('/api/sparql', { query });

    if (!data || !data.results || data.results.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-sm">No CSV level data available. Check that navis:hasLevel is present.</p>';
        return;
    }

    // Calculate total for percentages
    const total = data.results.reduce((sum, row) => sum + parseInt(row.count), 0);

    // Render level distribution
    let html = `<div class="text-xs text-gray-400 mb-3">Original Navisworks hierarchy depth</div>`;
    html += '<div class="space-y-2">';

    // Color gradient from purple to blue
    const colors = ['#c084fc', '#a78bfa', '#818cf8', '#6366f1', '#4f46e5', '#4338ca', '#3730a3', '#312e81'];

    data.results.forEach((row, i) => {
        const level = row.level;
        const count = parseInt(row.count);
        const pct = ((count / total) * 100).toFixed(1);
        const color = colors[Math.min(i, colors.length - 1)];

        html += `
            <div class="flex items-center gap-2">
                <span class="text-xs w-6" style="color:${color}">L${level}</span>
                <div class="flex-1 h-4 rounded" style="background:#0f172a">
                    <div class="h-full rounded" style="width:${pct}%; background:${color}"></div>
                </div>
                <span class="text-xs text-gray-400 w-16 text-right">${count.toLocaleString()}</span>
                <span class="text-xs text-gray-500 w-10 text-right">${pct}%</span>
            </div>`;
    });

    html += '</div>';
    html += `<div class="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-400">
        <strong>Total:</strong> ${total.toLocaleString()} elements<br>
        <span class="text-yellow-400">Note:</span> CSV ParentId is flattened (all → root)
    </div>`;

    container.innerHTML = html;
}

async function loadHierarchyTree() {
    const container = document.getElementById('hierarchy-tree-view');
    const depthValue = coerceInt(document.getElementById('hierarchy-depth')?.value);
    const maxDepth = depthValue || metadataCache.maxLevel || DEFAULT_MAX_LEVEL;

    container.innerHTML = '<div class="loading"><div class="spinner"></div>Building system path tree...</div>';

    // Optimized query using pre-computed hasElementCount
    const query = `
PREFIX navis: <http://example.org/bim-ontology/navis#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sp3d: <http://example.org/bim-ontology/sp3d#>

SELECT ?path ?name ?type ?children
WHERE {
    ?node a ?type ;
          rdfs:label ?name ;
          sp3d:hasSystemPath ?path ;
          navis:hasElementCount ?children .
    FILTER(?type IN (navis:Project, navis:Area, navis:Unit, navis:System))
}
ORDER BY ?path
LIMIT 500`;

    const data = await apiPost('/api/sparql', { query });

    if (!data || !data.results) {
        container.innerHTML = '<p class="text-red-400">Failed to load system path hierarchy.</p>';
        return;
    }

    hierarchyDrillData = buildHierarchyDrillData(data.results, maxDepth);
    renderSystemPathTree();
}

async function loadHierarchyNodeDetail(path, name) {
    const container = document.getElementById('hierarchy-details');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading elements for this path...</div>';

    // Query elements in this path (including original CSV Level)
    const query = `
PREFIX navis: <http://example.org/bim-ontology/navis#>
PREFIX sp3d: <http://example.org/bim-ontology/sp3d#>
PREFIX bim: <http://example.org/bim-ontology/schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?name ?category ?status ?level
WHERE {
    ?elem a navis:SP3DEntity ;
          rdfs:label ?name ;
          sp3d:hasSystemPath ?path .
    FILTER(STRSTARTS(?path, "${path}"))
    OPTIONAL { ?elem bim:hasCategory ?category }
    OPTIONAL { ?elem sp3d:hasStatus ?status }
    OPTIONAL { ?elem navis:hasLevel ?level }
}
ORDER BY ?level ?name
LIMIT 50`;

    const data = await apiPost('/api/sparql', { query });

    let html = `<h4 class="text-sm font-semibold text-blue-400 mb-3">${name} <span class="text-xs text-gray-500">(${path})</span></h4>`;

    if (!data || !data.results || data.results.length === 0) {
        html += '<p class="text-gray-500 text-sm">No elements found in this path. Try a higher-level node.</p>';
    } else {
        // Level distribution summary
        const levelCounts = {};
        data.results.forEach(row => {
            const lvl = row.level ?? 'N/A';
            levelCounts[lvl] = (levelCounts[lvl] || 0) + 1;
        });
        html += '<div class="mb-3"><span class="text-xs text-gray-400">CSV Levels: </span>';
        Object.entries(levelCounts).sort((a, b) => a[0] - b[0]).forEach(([lvl, cnt]) => {
            html += `<span class="badge badge-gray text-xs ml-1">L${lvl}: ${cnt}</span>`;
        });
        html += '</div>';

        html += '<table><thead><tr><th>Name</th><th>Category</th><th>CSV Level</th><th>Status</th></tr></thead><tbody>';
        data.results.forEach(row => {
            const levelBadge = row.level != null
                ? `<span class="badge" style="background:#4f46e522;color:#818cf8">L${row.level}</span>`
                : '<span class="text-gray-600">-</span>';
            html += `<tr>
                <td class="text-sm">${row.name || '-'}</td>
                <td><span class="badge badge-blue">${row.category || '-'}</span></td>
                <td>${levelBadge}</td>
                <td class="text-xs text-gray-400">${row.status || '-'}</td>
            </tr>`;
        });
        html += '</tbody></table>';
        if (data.results.length >= 50) {
            html += '<p class="text-xs text-gray-500 mt-2">Showing first 50 elements...</p>';
        }
    }

    container.innerHTML = html;
}

// ── Navis Miller Columns Drill-down ──

let navisDrillData = null;
let navisDrillState = { selectedUris: [] };
let navisSelectedUri = null;
const NAVIS_LEVEL_COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#06b6d4', '#84cc16', '#a855f7'];

function resetNavisDrilldown() {
    navisDrillState.selectedUris = [];
    navisSelectedUri = null;
    renderNavisDrilldown();
    document.getElementById('navis-aggregation-card').style.display = 'none';
    document.getElementById('navis-graph-card').style.display = 'none';
    const details = document.getElementById('hierarchy-details');
    if (details) details.innerHTML = '<p class="text-gray-500 text-sm">Select a node from the tree to view details.</p>';
}

function buildNavisDrillData(rows) {
    const nodesByUri = new Map();
    const childrenByUri = new Map();
    const roots = [];

    rows.forEach(row => {
        const uri = row.node;
        nodesByUri.set(uri, {
            uri,
            name: row.name,
            level: parseInt(row.level) || 0,
            parentUri: row.parent || null,
            childCount: parseInt(row.children) || 0,
            descendants: parseInt(row.descendants) || 0,
        });
    });

    nodesByUri.forEach(node => {
        if (node.parentUri && nodesByUri.has(node.parentUri)) {
            if (!childrenByUri.has(node.parentUri)) childrenByUri.set(node.parentUri, []);
            childrenByUri.get(node.parentUri).push(node);
        } else {
            roots.push(node);
        }
    });

    const sortNodes = list => list.sort((a, b) => b.descendants - a.descendants || a.name.localeCompare(b.name));
    sortNodes(roots);
    childrenByUri.forEach(sortNodes);

    return { nodesByUri, childrenByUri, roots };
}

function renderNavisDrilldown() {
    const container = document.getElementById('navis-tree-view');
    const breadcrumb = document.getElementById('navis-breadcrumb');
    if (!container || !breadcrumb) return;

    container.innerHTML = '';
    breadcrumb.innerHTML = '';

    if (!navisDrillData || navisDrillData.roots.length === 0) {
        container.innerHTML = '<div class="miller-empty">No nodes found. Load a file or increase depth.</div>';
        return;
    }

    // Build columns: root + each selected level
    const columns = [{ label: 'Root', nodes: navisDrillData.roots, parentUri: null }];
    navisDrillState.selectedUris.forEach((uri, idx) => {
        const children = navisDrillData.childrenByUri.get(uri) || [];
        const node = navisDrillData.nodesByUri.get(uri);
        columns.push({ label: node ? node.name : `Level ${idx + 2}`, nodes: children, parentUri: uri });
    });

    const totalCols = columns.length;
    // Wider last column, narrower previous ones
    columns.forEach((col, colIdx) => {
        const colEl = document.createElement('div');
        colEl.className = 'miller-column';
        const isLast = colIdx === totalCols - 1;
        const width = isLast ? Math.max(260, 400 - (totalCols - 1) * 20) : Math.max(140, 220 - (totalCols - 1) * 15);
        colEl.style.flex = isLast ? '1 0 260px' : `0 0 ${width}px`;
        colEl.style.minWidth = `${Math.max(140, width)}px`;

        const header = document.createElement('div');
        header.className = 'miller-column-header';
        const node = colIdx > 0 ? navisDrillData.nodesByUri.get(navisDrillState.selectedUris[colIdx - 1]) : null;
        header.textContent = colIdx === 0 ? 'Root' : (node ? `L${node.level} - ${node.name.substring(0, 20)}` : `Level ${colIdx}`);
        colEl.appendChild(header);

        const list = document.createElement('div');
        list.className = 'miller-column-list';

        if (!col.nodes || col.nodes.length === 0) {
            const empty = document.createElement('div');
            empty.className = 'miller-empty';
            empty.textContent = 'No children (leaf level)';
            list.appendChild(empty);
        } else {
            col.nodes.forEach(n => {
                const item = document.createElement('div');
                item.className = 'miller-item';
                if (navisDrillState.selectedUris[colIdx] === n.uri) item.classList.add('selected');

                const color = NAVIS_LEVEL_COLORS[Math.min(n.level, NAVIS_LEVEL_COLORS.length - 1)];

                const icon = document.createElement('span');
                icon.className = 'node-icon';
                icon.style.background = color;

                const name = document.createElement('span');
                name.className = 'miller-name';
                name.textContent = n.name || 'Unnamed';
                name.title = n.name;

                const badge = document.createElement('span');
                badge.className = 'badge';
                badge.style.background = `${color}22`;
                badge.style.color = color;
                badge.textContent = `L${n.level}`;

                const count = document.createElement('span');
                count.className = 'text-xs text-gray-500';
                count.textContent = n.descendants > 0 ? `(${n.descendants.toLocaleString()})` : n.childCount > 0 ? `(${n.childCount})` : '';

                item.appendChild(icon);
                item.appendChild(name);
                item.appendChild(badge);
                if (count.textContent) item.appendChild(count);

                item.addEventListener('click', () => selectNavisNode(colIdx, n.uri));
                list.appendChild(item);
            });
        }

        colEl.appendChild(list);
        container.appendChild(colEl);
    });

    // Scroll to last column
    requestAnimationFrame(() => container.scrollLeft = container.scrollWidth);

    // Update breadcrumb
    const rootCrumb = document.createElement('span');
    rootCrumb.className = 'crumb';
    rootCrumb.textContent = 'Root';
    rootCrumb.addEventListener('click', () => resetNavisDrilldown());
    breadcrumb.appendChild(rootCrumb);

    navisDrillState.selectedUris.forEach((uri, idx) => {
        const sep = document.createElement('span');
        sep.className = 'crumb-sep';
        sep.textContent = '>';
        breadcrumb.appendChild(sep);

        const node = navisDrillData.nodesByUri.get(uri);
        const crumb = document.createElement('span');
        crumb.className = 'crumb';
        crumb.textContent = node ? node.name.substring(0, 25) : 'Unknown';
        crumb.title = node ? node.name : '';
        crumb.addEventListener('click', () => {
            navisDrillState.selectedUris = navisDrillState.selectedUris.slice(0, idx + 1);
            navisSelectedUri = uri;
            renderNavisDrilldown();
            loadNavisNodeDetail(uri);
            loadNavisAggregation();
        });
        breadcrumb.appendChild(crumb);
    });
}

function selectNavisNode(colIdx, uri) {
    navisDrillState.selectedUris = navisDrillState.selectedUris.slice(0, colIdx);
    navisDrillState.selectedUris[colIdx] = uri;
    navisSelectedUri = uri;
    renderNavisDrilldown();
    loadNavisNodeDetail(uri);
    loadNavisAggregation();
}

async function loadNavisHierarchyTree() {
    const container = document.getElementById('navis-tree-view');
    const depthValue = coerceInt(document.getElementById('navis-depth')?.value);
    const maxDepth = depthValue || metadataCache.maxLevel || DEFAULT_MAX_LEVEL;

    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading Navisworks hierarchy...</div>';

    const query = `
PREFIX navis: <http://example.org/bim-ontology/navis#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?node ?name ?level ?parent ?children ?descendants WHERE {
    ?node navis:hasLevel ?level ; rdfs:label ?name .
    FILTER(?level <= ${maxDepth})
    OPTIONAL { ?node navis:hasParent ?parent }
    OPTIONAL { ?node navis:hasChildCount ?children }
    OPTIONAL { ?node navis:hasDescendantCount ?descendants }
    FILTER(BOUND(?parent) || BOUND(?children))
} ORDER BY ?level ?name LIMIT 15000`;

    const data = await apiPost('/api/sparql', { query });

    if (!data || !data.results || data.results.length === 0) {
        container.innerHTML = '<div class="miller-empty">No Navisworks nodes found. Try increasing depth or select another file.</div>';
        return;
    }

    navisDrillData = buildNavisDrillData(data.results);
    navisDrillState.selectedUris = [];
    navisSelectedUri = null;
    renderNavisDrilldown();
}

async function loadNavisNodeDetail(nodeUri) {
    const container = document.getElementById('hierarchy-details');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading node details...</div>';

    const query = `
PREFIX navis: <http://example.org/bim-ontology/navis#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX bim: <http://example.org/bim-ontology/schema#>
SELECT ?name ?level ?category ?children ?descendants WHERE {
    ?child navis:hasParent <${nodeUri}> ; rdfs:label ?name ; navis:hasLevel ?level .
    OPTIONAL { ?child bim:hasCategory ?category }
    OPTIONAL { ?child navis:hasChildCount ?children }
    OPTIONAL { ?child navis:hasDescendantCount ?descendants }
} ORDER BY DESC(?descendants) ?name LIMIT 100`;

    const data = await apiPost('/api/sparql', { query });

    const parentQuery = `
PREFIX navis: <http://example.org/bim-ontology/navis#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?name ?level ?children ?descendants WHERE {
    <${nodeUri}> rdfs:label ?name ; navis:hasLevel ?level .
    OPTIONAL { <${nodeUri}> navis:hasChildCount ?children }
    OPTIONAL { <${nodeUri}> navis:hasDescendantCount ?descendants }
}`;
    const parentData = await apiPost('/api/sparql', { query: parentQuery });

    let pName = nodeUri.split('/').pop(), pLevel = '?', pChildren = 0, pDesc = 0;
    if (parentData?.results?.[0]) {
        const r = parentData.results[0];
        pName = r.name; pLevel = r.level;
        pChildren = parseInt(r.children) || 0; pDesc = parseInt(r.descendants) || 0;
    }

    let html = `<h4 class="text-sm font-semibold text-blue-400 mb-2">${pName}
        <span class="badge badge-purple ml-2">L${pLevel}</span>
        <span class="text-xs text-gray-400 ml-2">(${pChildren} direct, ${pDesc.toLocaleString()} total)</span></h4>`;

    if (!data?.results?.length) {
        html += '<p class="text-gray-500 text-sm">Leaf node - no children.</p>';
    } else {
        html += '<table><thead><tr><th>Name</th><th>Level</th><th>Category</th><th>Direct</th><th>Total</th></tr></thead><tbody>';
        data.results.forEach(r => {
            html += `<tr><td class="text-sm">${r.name || '-'}</td>
                <td><span class="badge badge-purple">L${r.level}</span></td>
                <td><span class="badge badge-blue">${r.category || '-'}</span></td>
                <td class="text-right">${parseInt(r.children) || 0}</td>
                <td class="text-right text-green-400">${(parseInt(r.descendants) || 0).toLocaleString()}</td></tr>`;
        });
        html += '</tbody></table>';
    }

    // PropertyValue section for the selected node
    const pvQuery = `
PREFIX prop: <http://example.org/bim-ontology/property#>
SELECT ?category ?propName ?rawValue ?dataType ?unit WHERE {
    <${nodeUri}> prop:hasProperty ?pv .
    ?pv prop:propertyName ?propName ; prop:rawValue ?rawValue .
    OPTIONAL { ?pv prop:category ?category }
    OPTIONAL { ?pv prop:dataType ?dataType }
    OPTIONAL { ?pv prop:unit ?unit }
} ORDER BY ?category ?propName`;

    const pvData = await apiPost('/api/sparql', { query: pvQuery });

    if (pvData?.results?.length) {
        const cats = {};
        pvData.results.forEach(r => {
            const cat = r.category || 'Other';
            if (!cats[cat]) cats[cat] = [];
            cats[cat].push(r);
        });

        html += '<h5 class="text-xs text-gray-400 mt-4 mb-2">PropertyValues (' + pvData.results.length + ' properties)</h5>';
        Object.entries(cats).forEach(([cat, props]) => {
            const catId = 'pv-cat-' + cat.replace(/[^a-zA-Z0-9]/g, '_');
            html += `<details class="mb-2" open><summary class="cursor-pointer text-sm font-semibold text-blue-300">${cat} (${props.length})</summary>`;
            html += '<table class="mt-1"><thead><tr><th>Property</th><th>Value</th><th>Type</th><th>Unit</th></tr></thead><tbody>';
            props.forEach(p => {
                html += `<tr><td class="text-xs">${p.propName}</td>
                    <td class="text-xs text-green-400">${p.rawValue || '-'}</td>
                    <td class="text-xs text-gray-400">${p.dataType || '-'}</td>
                    <td class="text-xs text-gray-400">${p.unit || '-'}</td></tr>`;
            });
            html += '</tbody></table></details>';
        });
    } else {
        html += '<p class="text-xs text-gray-500 mt-4">No PropertyValues for this node. (PropertyValues require navis-via-csv-v3.ttl)</p>';
    }

    container.innerHTML = html;
}

// ── Property Aggregation ──

async function loadNavisAggregation() {
    if (!navisSelectedUri) return;
    const card = document.getElementById('navis-aggregation-card');
    const container = document.getElementById('navis-aggregation');
    const title = document.getElementById('navis-agg-title');
    card.style.display = 'block';

    const node = navisDrillData?.nodesByUri.get(navisSelectedUri);
    title.textContent = `Property Summary: ${node ? node.name : 'Selected Node'}`;
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Aggregating properties...</div>';

    let html = '';

    // 1) Subtree summary: category & status breakdown of descendants
    const subtreeQuery = `
PREFIX navis: <http://example.org/bim-ontology/navis#>
PREFIX bim: <http://example.org/bim-ontology/schema#>
PREFIX sp3d: <http://example.org/bim-ontology/sp3d#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?category (COUNT(?obj) as ?count) (SAMPLE(?status) as ?sampleStatus) WHERE {
    ?obj navis:hasParent* <${navisSelectedUri}> .
    OPTIONAL { ?obj bim:hasCategory ?category }
    OPTIONAL { ?obj sp3d:hasStatus ?status }
} GROUP BY ?category ORDER BY DESC(?count) LIMIT 20`;

    const subtreeData = await apiPost('/api/sparql', { query: subtreeQuery });

    if (subtreeData?.results?.length) {
        const total = subtreeData.results.reduce((s, r) => s + (parseInt(r.count) || 0), 0);
        html += '<div class="mb-4"><h5 class="text-xs text-gray-400 mb-2">Subtree Breakdown (' + total.toLocaleString() + ' objects)</h5>';
        html += '<table><thead><tr><th>Category</th><th>Count</th><th>%</th><th>Sample Status</th></tr></thead><tbody>';
        subtreeData.results.forEach(r => {
            const cnt = parseInt(r.count) || 0;
            const pct = total > 0 ? ((cnt / total) * 100).toFixed(1) : '0';
            html += `<tr><td><span class="badge badge-blue">${r.category || 'N/A'}</span></td>
                <td class="text-right">${cnt.toLocaleString()}</td>
                <td class="text-right text-gray-400">${pct}%</td>
                <td class="text-xs text-gray-400">${r.sampleStatus || '-'}</td></tr>`;
        });
        html += '</tbody></table></div>';
    }

    // 2) Status breakdown for subtree
    const statusQuery = `
PREFIX navis: <http://example.org/bim-ontology/navis#>
PREFIX sp3d: <http://example.org/bim-ontology/sp3d#>
SELECT ?status (COUNT(?obj) as ?count) WHERE {
    ?obj navis:hasParent* <${navisSelectedUri}> ;
         sp3d:hasStatus ?status .
} GROUP BY ?status ORDER BY DESC(?count)`;

    const statusData = await apiPost('/api/sparql', { query: statusQuery });

    if (statusData?.results?.length) {
        html += '<div class="mb-4"><h5 class="text-xs text-gray-400 mb-2">Status Distribution</h5>';
        html += '<div class="flex flex-wrap gap-2">';
        statusData.results.forEach(r => {
            const cnt = parseInt(r.count) || 0;
            const colorMap = { Working: '#4ade80', Approved: '#60a5fa', 'For Review': '#fbbf24' };
            const color = colorMap[r.status] || '#94a3b8';
            html += `<span class="badge" style="background:${color}22;color:${color}">${r.status}: ${cnt.toLocaleString()}</span>`;
        });
        html += '</div></div>';
    }

    // 3) Numeric PropertyValue aggregation (direct children only, for performance)
    const numericQuery = `
PREFIX navis: <http://example.org/bim-ontology/navis#>
PREFIX prop: <http://example.org/bim-ontology/property#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?propName (SUM(xsd:double(?rawValue)) as ?total) (AVG(xsd:double(?rawValue)) as ?avg) (COUNT(?pv) as ?cnt) (SAMPLE(?unit) as ?sampleUnit) WHERE {
    ?child navis:hasParent <${navisSelectedUri}> .
    ?child prop:hasProperty ?pv .
    ?pv prop:propertyName ?propName ; prop:rawValue ?rawValue ; prop:dataType "Double" .
    OPTIONAL { ?pv prop:unit ?unit }
    VALUES ?propName { "Dry Weight" "Area" "Length" "Width" "Volume" "Design Max Pressure" "Design Max Temperature" "Nominal Diameter" }
} GROUP BY ?propName ORDER BY ?propName`;

    const numericData = await apiPost('/api/sparql', { query: numericQuery });

    if (numericData?.results?.length) {
        html += '<h5 class="text-xs text-gray-400 mb-2">Numeric Aggregation (Direct Children)</h5>';
        html += '<div class="grid grid-cols-2 gap-2">';
        numericData.results.forEach(r => {
            const total = parseFloat(r.total);
            const avg = parseFloat(r.avg);
            const cnt = parseInt(r.cnt) || 0;
            const unit = r.sampleUnit || '';
            const fmtTotal = isNaN(total) ? '-' : total.toLocaleString(undefined, {maximumFractionDigits: 2});
            const fmtAvg = isNaN(avg) ? '-' : avg.toLocaleString(undefined, {maximumFractionDigits: 2});
            html += `<div class="card p-2">
                <div class="text-xs text-gray-400">${r.propName} ${unit ? '(' + unit + ')' : ''}</div>
                <div class="text-sm font-bold text-green-400">SUM: ${fmtTotal}</div>
                <div class="text-xs text-blue-300">AVG: ${fmtAvg} | Count: ${cnt}</div></div>`;
        });
        html += '</div>';
    }

    // 4) PropertyValue pattern summary by category (v3 file only)
    const propQuery = `
PREFIX navis: <http://example.org/bim-ontology/navis#>
PREFIX prop: <http://example.org/bim-ontology/property#>
SELECT ?category ?propName (COUNT(?pv) as ?count) (SAMPLE(?raw) as ?sampleValue) WHERE {
    ?child navis:hasParent <${navisSelectedUri}> .
    ?child prop:hasProperty ?pv .
    ?pv prop:propertyName ?propName .
    ?pv prop:rawValue ?raw .
    OPTIONAL { ?pv prop:category ?category }
} GROUP BY ?category ?propName ORDER BY ?category ?propName LIMIT 50`;

    const propData = await apiPost('/api/sparql', { query: propQuery });

    if (propData?.results?.length) {
        const categories = {};
        propData.results.forEach(r => {
            const cat = r.category || 'Other';
            if (!categories[cat]) categories[cat] = [];
            categories[cat].push({ name: r.propName, count: parseInt(r.count) || 0, sample: r.sampleValue });
        });

        html += '<h5 class="text-xs text-gray-400 mt-3 mb-2">Property Values by Category (Direct Children)</h5>';
        Object.entries(categories).forEach(([cat, props]) => {
            html += `<details class="mb-2"><summary class="cursor-pointer text-sm font-semibold text-blue-300">${cat} (${props.length} properties)</summary>`;
            html += '<table class="mt-1"><thead><tr><th>Property</th><th>Count</th><th>Sample</th></tr></thead><tbody>';
            props.forEach(p => {
                html += `<tr><td class="text-xs">${p.name}</td><td class="text-right">${p.count}</td><td class="text-xs text-green-400">${p.sample || '-'}</td></tr>`;
            });
            html += '</tbody></table></details>';
        });
    }

    if (!html) {
        html = '<p class="text-gray-500 text-sm">No property data found for this subtree.</p>';
    }

    container.innerHTML = html;
}

// ── Graph Toggle ──

function toggleNavisGraph() {
    const card = document.getElementById('navis-graph-card');
    const btn = document.getElementById('navis-graph-btn');
    if (card.style.display === 'none') {
        card.style.display = 'block';
        btn.textContent = 'Hide Graph';
        renderNavisGraph();
    } else {
        card.style.display = 'none';
        btn.textContent = 'Show Graph';
    }
}

function renderNavisGraph() {
    const canvas = document.getElementById('navis-graph-canvas');
    if (!canvas || !navisDrillData) return;
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Simple tree graph: show selected path + children
    const nodesToDraw = [];
    const edges = [];

    // Add roots
    const displayNodes = navisDrillState.selectedUris.length > 0
        ? [navisDrillState.selectedUris[navisDrillState.selectedUris.length - 1]]
        : navisDrillData.roots.slice(0, 5).map(n => n.uri);

    displayNodes.forEach(uri => {
        const node = navisDrillData.nodesByUri.get(uri);
        if (!node) return;
        nodesToDraw.push({ ...node, x: 0, y: 0 });

        const children = navisDrillData.childrenByUri.get(uri) || [];
        children.slice(0, 12).forEach(child => {
            nodesToDraw.push({ ...child, x: 0, y: 0 });
            edges.push({ from: uri, to: child.uri });
        });
    });

    if (nodesToDraw.length === 0) {
        ctx.fillStyle = '#64748b';
        ctx.font = '14px sans-serif';
        ctx.fillText('Select a node to view graph', 20, 30);
        return;
    }

    // Layout: parent center, children in arc below
    const centerX = canvas.width / 2;
    const centerY = 60;
    const parent = nodesToDraw[0];
    parent.x = centerX;
    parent.y = centerY;

    const childNodes = nodesToDraw.slice(1);
    const radius = Math.min(canvas.width * 0.4, 250);
    childNodes.forEach((child, i) => {
        const angle = Math.PI * (0.2 + 0.6 * i / Math.max(childNodes.length - 1, 1));
        child.x = centerX + radius * Math.cos(angle) * (i % 2 === 0 ? 1 : -1) * ((i + 1) / childNodes.length);
        child.y = centerY + 80 + radius * Math.sin(angle) * 0.8;
    });

    // Draw edges
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 1;
    edges.forEach(e => {
        const from = nodesToDraw.find(n => n.uri === e.from);
        const to = nodesToDraw.find(n => n.uri === e.to);
        if (from && to) {
            ctx.beginPath();
            ctx.moveTo(from.x, from.y);
            ctx.lineTo(to.x, to.y);
            ctx.stroke();
        }
    });

    // Draw nodes
    nodesToDraw.forEach((n, i) => {
        const color = NAVIS_LEVEL_COLORS[Math.min(n.level, NAVIS_LEVEL_COLORS.length - 1)];
        const r = i === 0 ? 20 : 12;
        ctx.beginPath();
        ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = '#0f172a';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Label
        ctx.fillStyle = '#e2e8f0';
        ctx.font = i === 0 ? 'bold 12px sans-serif' : '10px sans-serif';
        ctx.textAlign = 'center';
        const label = n.name.length > 18 ? n.name.substring(0, 18) + '..' : n.name;
        ctx.fillText(label, n.x, n.y + r + 14);

        if (n.descendants > 0) {
            ctx.fillStyle = '#64748b';
            ctx.font = '9px sans-serif';
            ctx.fillText(`(${n.descendants.toLocaleString()})`, n.x, n.y + r + 26);
        }
    });
}

async function initHierarchyTab() {
    if (!metadataCache.maxLevel) {
        await loadMaxLevel();
    }
    updateDepthSelectors(metadataCache.maxLevel);
    loadHierarchyFiles();
    loadHierarchyComparison();
    loadLevelDistribution();
    loadHierarchyTree();
    loadNavisHierarchyTree();
}

// ── Init ──

initQueryTemplates();
checkHealth();
loadOverviewFiles();
loadOverview();
loadMaxLevel();
ensureTabState('overview').initialized = true;
