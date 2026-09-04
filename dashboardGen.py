from flask import Flask, render_template, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fleet Intelligence Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.sheetjs.com/xlsx-0.20.2/package/dist/xlsx.full.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Inter', sans-serif;
            background: #f4f6fc;
            padding: 20px 16px;
            color: #1a2b4c;
        }
        .container {
            max-width: 1440px;
            margin: 0 auto;
        }
        .hero-header {
            background: linear-gradient(135deg, #0b1e3a 0%, #1f3a60 100%);
            border-radius: 36px;
            padding: 2rem 2.5rem;
            margin-bottom: 2rem;
            color: white;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
        }
        .hero-left h1 {
            font-size: 2rem;
            font-weight: 800;
        }
        .hero-btn {
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.25);
            padding: 10px 20px;
            border-radius: 40px;
            color: white;
            cursor: pointer;
        }
        .hero-btn.primary {
            background: #f0b90b;
            color: #0b1e3a;
            border: none;
        }
        .upload-card {
            max-width: 900px;
            margin: 0 auto 2.5rem auto;
            background: white;
            border-radius: 2rem;
            padding: 2rem 2.5rem;
            text-align: center;
        }
        .upload-button {
            background: #eef2ff;
            border: 2px dashed #b9c8e0;
            border-radius: 20px;
            padding: 2rem;
            cursor: pointer;
            display: inline-block;
        }
        #dashboard {
            display: none;
        }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 18px;
            margin-bottom: 28px;
        }
        .kpi-card {
            background: white;
            border-radius: 20px;
            padding: 18px;
            border: 1px solid #eef2f8;
            text-align: center;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: 800;
            color: #1e293b;
        }
        .kpi-loss {
            color: #dc2626;
        }
        .filters {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 28px;
        }
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .filter-group label {
            font-size: 10px;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
        }
        select, input, button {
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 0.85rem;
            border: 1px solid #e2e8f0;
            background: white;
        }
        button {
            background: #1e3a5f;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
        }
        .reset-btn {
            background: #f1f5f9;
            color: #1e293b;
            border: 1px solid #e2e8f0;
        }
        .table-wrapper {
            background: white;
            border-radius: 20px;
            overflow-x: auto;
            max-height: 480px;
            border: 1px solid #eef2f8;
            margin-bottom: 28px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.8rem;
        }
        th {
            background: #f8fafc;
            padding: 14px 8px;
            font-weight: 700;
            border-bottom: 2px solid #e2e8f0;
            position: sticky;
            top: 0;
        }
        td {
            padding: 10px 8px;
            border-bottom: 1px solid #f1f5f9;
        }
        .critical-row {
            background-color: #fee2e2;
        }
        .warning-row {
            background-color: #fef3c7;
        }
        .map-container {
            background: white;
            border-radius: 24px;
            padding: 24px;
            margin-bottom: 28px;
            border: 1px solid #eef2f8;
        }
        #map {
            height: 400px;
            border-radius: 16px;
        }
        .toast {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #10b981;
            color: white;
            padding: 12px 24px;
            border-radius: 48px;
            z-index: 1000;
            display: none;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            justify-content: center;
            align-items: center;
            z-index: 2000;
        }
        .modal-content {
            background: white;
            border-radius: 28px;
            padding: 28px;
            max-width: 500px;
            text-align: center;
        }
        @media (max-width: 768px) {
            .kpi-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>

<div class="container">

    <div class="hero-header">
        <div class="hero-left">
            <h1>🚀 Fleet Intelligence Dashboard</h1>
            <div style="color: #b9c8e0;">Real-time asset performance & predictive analytics</div>
        </div>
        <div>
            <button class="hero-btn" onclick="document.getElementById('csvFile').click()">📤 Upload CSV</button>
            <button class="hero-btn primary" onclick="takeScreenshot()">📸 Screenshot</button>
        </div>
    </div>

    <input type="file" id="csvFile" accept=".csv" style="display:none;">

    <div class="upload-card" id="uploadCard">
        <h2>📊 Upload Your Fleet Data</h2>
        <div class="upload-button" id="uploadBtn">
            📁<br><strong>Choose File</strong><br><small>or drag & drop</small>
        </div>
    </div>

    <div id="dashboard">
        <div id="dataTimestamp" style="background:#eef2ff; padding:6px 16px; border-radius:20px; display:inline-block; margin-bottom:20px;"></div>

        <div class="kpi-grid" id="kpiGrid"></div>

        <div class="filters">
            <div class="filter-group"><label>Region</label><select id="regionFilter"><option value="all">All</option></select></div>
            <div class="filter-group"><label>Status</label><select id="riskFilter"><option value="all">All</option><option value="critical">Critical</option><option value="warning">Warning</option><option value="good">Good</option></select></div>
            <div class="filter-group"><label>Search</label><input type="text" id="searchInput" placeholder="Store, city..."></div>
            <button id="resetBtn" class="reset-btn">🔄 Reset</button>
        </div>

        <div class="table-wrapper">
            <table id="dataTable">
                <thead>
                    <tr>
                        <th>Store</th><th>Address</th><th>City</th><th>Region</th>
                        <th>Volume</th><th>Reject%</th><th>Uptime%</th><th>Loss</th>
                    </tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>

        <div class="map-container">
            <h3>📍 Asset Location Map</h3>
            <div id="map"></div>
        </div>
    </div>
</div>

<div id="toast" class="toast"></div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.sheetjs.com/xlsx-0.20.2/package/dist/xlsx.full.min.js"></script>
<script>
    let allData = [];
    let currentSort = { column: 'loss', direction: 'desc' };
    let map = null;

    function showToast(msg) {
        let t = document.getElementById('toast');
        t.textContent = msg;
        t.style.display = 'block';
        setTimeout(() => t.style.display = 'none', 3000);
    }

    function getStatusLevel(r) {
        let rej = parseFloat(r.Reject7Day) || 0;
        if (rej >= 8) return 'Critical';
        if (rej >= 4) return 'Warning';
        return 'Good';
    }

    function calcDailyLoss(r) {
        let vol = parseFloat(r.Tx1Day) || 0;
        let rej = parseFloat(r.Reject7Day) || 0;
        let uptime = parseFloat(r.Uptime7Day) || 100;
        return (vol * (rej / 100) * 5) + (vol * ((100 - uptime) / 100) * 4);
    }

    function getRegion(r) { return r.Province || r.State || 'Unknown'; }

    function getStoreId(r) { return (r.Store || '').replace(/[^a-zA-Z0-9]/g, '_'); }

    function parseCSV(text) {
        const lines = text.split(/\r?\n/);
        if (lines.length < 2) return false;
        let headers = lines[0].split(',').map(h => h.replace(/"/g, '').trim());
        let data = [];
        for (let i = 1; i < lines.length; i++) {
            if (!lines[i].trim()) continue;
            let row = {}, col = 0, cur = '', inQ = false;
            for (let ch of lines[i]) {
                if (ch === '"') inQ = !inQ;
                else if (ch === ',' && !inQ) { row[headers[col]] = cur.trim(); cur = ''; col++; }
                else cur += ch;
            }
            if (col < headers.length) row[headers[col]] = cur.trim();
            if (Object.keys(row).length) data.push(row);
        }
        if (!data.length) return false;
        allData = data.map(row => ({
            Store: row.Store || row['Store Name'] || 'Unknown',
            Address: row.Address || '',
            City: row.City || '',
            Province: row.State || row.Province || '',
            Tx1Day: row['1 Day TX'] || row.Volume || '0',
            Tx7Day: row['7 Day TX'] || '0',
            Reject7Day: row['7 Day Reject %'] || row.Reject7Day || '0',
            Uptime7Day: row['7 Day Uptime %'] || row.Uptime || '100',
            LastPM: row['Last PM Date'] || '',
            Latitude: row.Latitude || '',
            Longitude: row.Longitude || ''
        }));
        return true;
    }

    function renderAll() {
        if (!allData.length) return;
        let f = [...allData];
        let search = document.getElementById('searchInput')?.value.toLowerCase() || '';
        if (search) f = f.filter(r => (r.Store || '').toLowerCase().includes(search) || (r.City || '').toLowerCase().includes(search));
        let region = document.getElementById('regionFilter')?.value || 'all';
        if (region !== 'all') f = f.filter(r => getRegion(r) === region);
        let status = document.getElementById('riskFilter')?.value || 'all';
        if (status === 'critical') f = f.filter(r => getStatusLevel(r) === 'Critical');
        else if (status === 'warning') f = f.filter(r => getStatusLevel(r) === 'Warning');
        else if (status === 'good') f = f.filter(r => getStatusLevel(r) === 'Good');

        f = [...f].sort((a, b) => {
            let va = calcDailyLoss(a), vb = calcDailyLoss(b);
            return currentSort.direction === 'desc' ? vb - va : va - vb;
        });

        const total = f.length, crit = f.filter(r => getStatusLevel(r) === 'Critical').length;
        const warn = f.filter(r => getStatusLevel(r) === 'Warning').length;
        const tLoss = f.reduce((s, r) => s + calcDailyLoss(r), 0);

        document.getElementById('kpiGrid').innerHTML = `
            <div class="kpi-card"><div class="kpi-label">📊 Total Assets</div><div class="kpi-value">${total}</div></div>
            <div class="kpi-card"><div class="kpi-label">🔴 Critical</div><div class="kpi-value" style="color:#dc2626;">${crit}</div></div>
            <div class="kpi-card"><div class="kpi-label">🟡 Warning</div><div class="kpi-value" style="color:#f59e0b;">${warn}</div></div>
            <div class="kpi-card"><div class="kpi-label">💸 Daily Loss</div><div class="kpi-value kpi-loss">$${tLoss.toFixed(0)}</div></div>
        `;

        const tbody = document.getElementById('tableBody');
        if (!f.length) { tbody.innerHTML = '<tr><td colspan="8">No data</td></tr>'; return; }
        tbody.innerHTML = f.map(r => {
            const loss = calcDailyLoss(r), reject = parseFloat(r.Reject7Day) || 0;
            const statusClass = getStatusLevel(r) === 'Critical' ? 'critical-row' :
                               getStatusLevel(r) === 'Warning' ? 'warning-row' : '';
            return `<tr class="${statusClass}">
                <td>${r.Store || '—'}</td>
                <td>${r.Address || '—'}</td>
                <td>${r.City || '—'}</td>
                <td>${getRegion(r)}</td>
                <td>${parseFloat(r.Tx1Day) || 0}</td>
                <td>${reject.toFixed(1)}%</td>
                <td>${parseFloat(r.Uptime7Day || 100).toFixed(1)}%</td>
                <td style="color:#dc2626;">$${loss.toFixed(0)}</td>
            </tr>`;
        }).join('');

        updateMap(f);
    }

    function updateMap(data) {
        if (map) map.remove();
        map = L.map('map').setView([56.1304, -106.3468], 4);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { attribution: 'OSM' }).addTo(map);
        let bounds = [];
        data.forEach(r => {
            let lat = parseFloat(r.Latitude), lng = parseFloat(r.Longitude);
            if (!isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0) {
                let status = getStatusLevel(r);
                let color = status === 'Critical' ? '#dc2626' : status === 'Warning' ? '#f59e0b' : '#10b981';
                L.circleMarker([lat, lng], { radius: 8, fillColor: color, color: '#fff', weight: 2 })
                    .addTo(map)
                    .bindPopup(`<b>${r.Store}</b><br>Loss: $${calcDailyLoss(r).toFixed(0)}`);
                bounds.push([lat, lng]);
            }
        });
        if (bounds.length) map.fitBounds(bounds);
        else map.fitBounds([[42, -79], [50, -60]]);
        setTimeout(() => map.invalidateSize(), 100);
    }

    function populateFilters() {
        const regions = [...new Set(allData.map(r => getRegion(r)))].filter(r => r && r !== 'Unknown');
        document.getElementById('regionFilter').innerHTML = '<option value="all">All</option>' +
            regions.sort().map(p => `<option value="${p}">${p}</option>`).join('');
    }

    function takeScreenshot() {
        if (!allData.length) return showToast('No data');
        showToast('Capturing...');
        html2canvas(document.getElementById('dashboard')).then(canvas => {
            let link = document.createElement('a');
            link.download = 'dashboard_' + Date.now() + '.png';
            link.href = canvas.toDataURL();
            link.click();
            showToast('Screenshot saved');
        }).catch(() => showToast('Failed'));
    }

    document.getElementById('uploadBtn').addEventListener('click', () => document.getElementById('csvFile').click());
    document.getElementById('csvFile').addEventListener('change', e => {
        if (!e.target.files || !e.target.files[0]) return;
        const file = e.target.files[0];
        if (!file.name.endsWith('.csv')) return showToast('Please upload a CSV file');
        const reader = new FileReader();
        reader.onload = ev => {
            if (parseCSV(ev.target.result)) {
                document.getElementById('uploadCard').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                document.getElementById('dataTimestamp').textContent = '📅 ' + new Date().toLocaleString() + ' — ' + allData.length + ' assets';
                populateFilters();
                renderAll();
                showToast('Loaded ' + allData.length + ' assets');
            } else showToast('Invalid CSV');
        };
        reader.readAsText(file, 'UTF-8');
    });

    document.getElementById('resetBtn').addEventListener('click', () => {
        document.getElementById('regionFilter').value = 'all';
        document.getElementById('riskFilter').value = 'all';
        document.getElementById('searchInput').value = '';
        renderAll();
    });

    document.getElementById('searchInput').addEventListener('input', renderAll);
    document.getElementById('regionFilter').addEventListener('change', renderAll);
    document.getElementById('riskFilter').addEventListener('change', renderAll);

    // Load Leaflet
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    document.head.appendChild(script);
</script>
</body>
</html>
"""


@app.route('/')
def home():
    return HTML_TEMPLATE


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
