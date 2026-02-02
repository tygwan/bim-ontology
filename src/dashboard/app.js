/**
 * BIM Ontology Dashboard - Main Application
 */

const API_BASE = '';  // Same origin
let currentPage = 0;
const PAGE_SIZE = 50;
let categoryChart = null;
let barChart = null;

// ── Navigation ──

document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
        tab.classList.add('active');
        const target = document.getElementById('tab-' + tab.dataset.tab);
        if (target) target.style.display = 'block';

        // Lazy-load tab data
        const tabName = tab.dataset.tab;
        if (tabName === 'buildings') loadHierarchy();
        if (tabName === 'elements') { loadCategoryFilter(); loadElements(); }
    });
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
    const data = await api('/api/hierarchy');
    if (!data) {
        container.innerHTML = '<p class="text-gray-500 text-sm">Failed to load hierarchy.</p>';
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
    tbody.innerHTML = '<tr><td colspan="4" class="loading"><div class="spinner"></div>Loading...</td></tr>';

    let url = `/api/elements?limit=${PAGE_SIZE}&offset=${currentPage * PAGE_SIZE}`;
    if (category) url += `&category=${encodeURIComponent(category)}`;

    const data = await api(url);
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-gray-500">No elements found.</td></tr>';
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

// ── Init ──

initQueryTemplates();
checkHealth();
loadOverview();
