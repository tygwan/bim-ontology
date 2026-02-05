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
        if (tabName === 'hierarchy') initHierarchyTab();
        if (tabName === 'elements') { loadCategoryFilter(); loadElements(); }
        if (tabName === 'properties') loadPlantData();
        if (tabName === 'ontology') { loadOntologyTypes(); loadOntologyLinks(); loadRules(); }
        if (tabName === 'validation') loadTTLFiles();
        if (tabName === 'explorer') initExplorer();
        if (tabName === 'lean') loadLeanStats();
        if (tabName === 'todayswork') initTodaysWork();
        if (tabName === 'statusmon') initStatusMonitor();
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
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading...</div>';

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
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Searching...</div>';

    const data = await api(`/api/properties/search?key=${encodeURIComponent(key)}&limit=50`);
    if (!data || !data.results) {
        container.innerHTML = '<p class="text-gray-500 text-sm">No results.</p>';
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
    tbody.innerHTML = '<tr><td colspan="5" class="loading"><div class="spinner"></div>Loading...</td></tr>';

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
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-gray-500">No elements found.</td></tr>';
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
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading...</div>';

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
        container.innerHTML = '<span class="text-gray-500 text-xs">Failed to load predicates.</span>';
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
        tbody.innerHTML = '<tr><td class="text-gray-500">Select at least one column predicate.</td></tr>';
        thead.innerHTML = '<tr><th>subject</th></tr>';
        info.textContent = '--';
        pageInfo.textContent = '';
        return;
    }

    tbody.innerHTML = '<tr><td colspan="' + (columns.length + 1) + '" class="loading"><div class="spinner"></div>Loading...</td></tr>';

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
        tbody.innerHTML = '<tr><td colspan="' + (columns.length + 1) + '" class="text-center text-gray-500">No nodes found.</td></tr>';
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
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading...</div>';

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
    list.innerHTML = '<div class="loading"><div class="spinner"></div>Loading...</div>';

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

async function loadHierarchyComparison() {
    const container = document.getElementById('hierarchy-comparison');

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
        container.innerHTML = '<p class="text-red-400">Failed to load hierarchy stats</p>';
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

    container.innerHTML = `
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

async function loadHierarchyTree() {
    const container = document.getElementById('hierarchy-tree-view');
    const maxDepth = parseInt(document.getElementById('hierarchy-depth').value);

    container.innerHTML = '<div class="loading"><div class="spinner"></div>Building tree...</div>';

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
        container.innerHTML = '<p class="text-red-400">Failed to load hierarchy</p>';
        return;
    }

    // Build tree structure
    const tree = {};
    const typeColors = {
        'Project': '#8b5cf6',
        'Area': '#3b82f6',
        'Unit': '#10b981',
        'System': '#64748b'
    };

    data.results.forEach(row => {
        const path = row.path;
        const parts = path.split('\\\\');
        if (parts.length > maxDepth) return;

        const depth = parts.length - 1;
        const typeName = row.type.split('#').pop();

        if (!tree[depth]) tree[depth] = [];
        tree[depth].push({
            path: path,
            name: row.name,
            type: typeName,
            children: parseInt(row.children) || 0,
            color: typeColors[typeName] || '#94a3b8'
        });
    });

    // Render tree
    let html = '';

    // Group by depth and render
    for (let d = 0; d <= maxDepth; d++) {
        const nodes = tree[d] || [];
        if (nodes.length === 0) continue;

        const groupedByParent = {};
        nodes.forEach(n => {
            const parts = n.path.split('\\\\');
            const parentPath = parts.slice(0, -1).join('\\\\') || 'ROOT';
            if (!groupedByParent[parentPath]) groupedByParent[parentPath] = [];
            groupedByParent[parentPath].push(n);
        });

        Object.entries(groupedByParent).forEach(([parent, children]) => {
            children.sort((a, b) => b.children - a.children);
        });

        tree[d] = nodes;
    }

    // Render as nested HTML
    function renderNode(node, indent = 0) {
        const margin = indent * 20;
        return `
            <div class="hierarchy-tree-node" style="margin-left: ${margin}px; padding: 4px 8px; cursor: pointer; border-radius: 4px;"
                 onclick="loadHierarchyNodeDetail('${node.path.replace(/'/g, "\\'")}', '${node.name.replace(/'/g, "\\'")}')"
                 onmouseover="this.style.background='#334155'" onmouseout="this.style.background='transparent'">
                <span class="node-icon" style="background: ${node.color}"></span>
                <span class="text-sm">${node.name}</span>
                <span class="badge" style="background: ${node.color}22; color: ${node.color}; margin-left: 8px;">${node.type}</span>
                ${node.children > 0 ? `<span class="text-xs text-gray-500 ml-2">(${node.children})</span>` : ''}
            </div>`;
    }

    // Simple flat render with indentation
    const allNodes = [];
    data.results.forEach(row => {
        const path = row.path;
        const parts = path.split('\\\\');
        if (parts.length > maxDepth + 1) return;

        const typeName = row.type.split('#').pop();
        allNodes.push({
            path: path,
            name: row.name,
            type: typeName,
            children: parseInt(row.children) || 0,
            color: typeColors[typeName] || '#94a3b8',
            depth: parts.length - 1
        });
    });

    // Sort by path to maintain hierarchy order
    allNodes.sort((a, b) => a.path.localeCompare(b.path));

    html = allNodes.map(n => renderNode(n, n.depth)).join('');

    container.innerHTML = html || '<p class="text-gray-500">No hierarchy data found</p>';
}

async function loadHierarchyNodeDetail(path, name) {
    const container = document.getElementById('hierarchy-details');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading elements...</div>';

    // Query elements in this path
    const query = `
PREFIX navis: <http://example.org/bim-ontology/navis#>
PREFIX sp3d: <http://example.org/bim-ontology/sp3d#>
PREFIX bim: <http://example.org/bim-ontology/schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?name ?category ?status
WHERE {
    ?elem a navis:SP3DEntity ;
          rdfs:label ?name ;
          sp3d:hasSystemPath ?path .
    FILTER(STRSTARTS(?path, "${path}"))
    OPTIONAL { ?elem bim:hasCategory ?category }
    OPTIONAL { ?elem sp3d:hasStatus ?status }
}
LIMIT 50`;

    const data = await apiPost('/api/sparql', { query });

    let html = `<h4 class="text-sm font-semibold text-blue-400 mb-3">${name} <span class="text-xs text-gray-500">(${path})</span></h4>`;

    if (!data || !data.results || data.results.length === 0) {
        html += '<p class="text-gray-500 text-sm">No elements found in this path.</p>';
    } else {
        html += '<table><thead><tr><th>Name</th><th>Category</th><th>Status</th></tr></thead><tbody>';
        data.results.forEach(row => {
            html += `<tr>
                <td class="text-sm">${row.name || '-'}</td>
                <td><span class="badge badge-blue">${row.category || '-'}</span></td>
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

function initHierarchyTab() {
    loadHierarchyComparison();
    loadHierarchyTree();
}

// ── Init ──

initQueryTemplates();
checkHealth();
loadOverview();
