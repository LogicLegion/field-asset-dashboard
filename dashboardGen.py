from flask import Flask
import os

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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: #f4f6fc;
            padding: 20px 16px;
            color: #1a2b4c;
        }
        .container { max-width: 1440px; margin: 0 auto; }
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
        .hero-left h1 { font-size: 2rem; font-weight: 800; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
        .live-pulse {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(34, 197, 94, 0.25);
            padding: 5px 14px;
            border-radius: 40px;
            font-size: 0.75rem;
            font-weight: 600;
            color: #86efac;
            border: 1px solid rgba(34, 197, 94, 0.5);
        }
        .live-pulse::before {
            content: "";
            width: 8px;
            height: 8px;
            background: #22c55e;
            border-radius: 50%;
            display: inline-block;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse { 0% { opacity: 1; transform: scale(1); } 100% { opacity: 0.3; transform: scale(1.3); } }
        .hero-left .subtitle { color: #b9c8e0; margin-top: 8px; font-size: 0.95rem; }
        .hero-left .creator { color: #8899bb; font-size: 0.75rem; margin-top: 4px; }
        .hero-right { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
        .hero-btn {
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.25);
            padding: 10px 20px;
            border-radius: 40px;
            color: white;
            cursor: pointer;
            font-weight: 600;
            transition: 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.85rem;
        }
        .hero-btn:hover { background: rgba(255,255,255,0.25); transform: translateY(-2px); }
        .hero-btn.primary { background: #f0b90b; color: #0b1e3a; border: none; }
        .upload-card {
            max-width: 900px;
            margin: 0 auto 2.5rem auto;
            background: white;
            border-radius: 2rem;
            padding: 2rem 2.5rem;
            text-align: center;
            box-shadow: 0 20px 35px -10px rgba(0,0,0,0.08);
        }
        .upload-button {
            background: #eef2ff;
            border: 2px dashed #b9c8e0;
            border-radius: 20px;
            padding: 2rem;
            cursor: pointer;
            display: inline-block;
            transition: 0.2s;
        }
        .upload-button:hover { background: #e0e7ff; border-color: #4a5b6e; }
        #dashboard { display: none; }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 18px;
            margin-bottom: 28px;
        }
        .kpi-card {
            background: white;
            border-radius: 20px;
            padding: 18px;
            border: 1px solid #eef2f8;
            text-align: center;
            box-shadow: 0 6px 14px rgba(0,0,0,0.03);
            transition: 0.2s;
        }
        .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 12px 24px rgba(0,0,0,0.06); }
        .kpi-label { font-size: 11px; color: #64748b; text-transform: uppercase; margin-bottom: 6px; display: flex; align-items: center; justify-content: center; gap: 4px; }
        .kpi-value { font-size: 28px; font-weight: 800; color: #1e293b; }
        .kpi-loss { color: #dc2626; }
        .kpi-green { color: #10b981; }
        .filters {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 28px;
            align-items: flex-end;
            background: white;
            padding: 18px 20px;
            border-radius: 20px;
            border: 1px solid #eef2f8;
        }
        .filter-group { display: flex; flex-direction: column; gap: 6px; min-width: 120px; flex: 1; }
        .filter-group label { font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase; }
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
            transition: 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        button:hover { background: #13273f; }
        .reset-btn { background: #f1f5f9; color: #1e293b; border: 1px solid #e2e8f0; }
        .table-wrapper {
            background: white;
            border-radius: 20px;
            overflow-x: auto;
            max-height: 480px;
            border: 1px solid #eef2f8;
            margin-bottom: 28px;
        }
        table { width: 100%; border-collapse: collapse; font-size: 0.8rem; min-width: 1200px; }
        th {
            background: #f8fafc;
            padding: 14px 10px;
            font-weight: 700;
            border-bottom: 2px solid #e2e8f0;
            position: sticky;
            top: 0;
            white-space: nowrap;
            text-align: left;
        }
        td { padding: 10px 10px; border-bottom: 1px solid #f1f5f9; white-space: nowrap; }
        .critical-row { background-color: #fee2e2; }
        .warning-row { background-color: #fef3c7; }
        .good-row { background-color: #dcfce7; }
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 30px;
            font-size: 10px;
            font-weight: 600;
        }
        .badge-critical { background: #dc2626; color: white; }
        .badge-warning { background: #f59e0b; color: white; }
        .badge-good { background: #10b981; color: white; }
        .badge-offline { background: #6b7280; color: white; }
        .badge-high { background: #dc2626; color: white; }
        .badge-mid { background: #f59e0b; color: white; }
        .badge-low { background: #10b981; color: white; }
        .map-container {
            background: white;
            border-radius: 24px;
            padding: 24px;
            margin-bottom: 28px;
            border: 1px solid #eef2f8;
        }
        #map { height: 400px; border-radius: 16px; }
        .map-legend { display: flex; justify-content: center; gap: 20px; margin-top: 12px; font-size: 11px; flex-wrap: wrap; }
        .map-legend-dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 4px; }
        .toast {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #10b981;
            color: white;
            padding: 12px 24px;
            border-radius: 48px;
            font-size: 13px;
            z-index: 1000;
            display: none;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        .call-btn {
            background: #e2e8f0;
            border: none;
            padding: 4px 8px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
        }
        .call-btn:hover { background: #cbd5e1; }
        @media (max-width: 768px) {
            .hero-header { flex-direction: column; text-align: center; }
            .kpi-grid { grid-template-columns: repeat(2, 1fr); }
            .filters { flex-direction: column; }
            .filter-group { min-width: 100%; }
        }
    </style>
</head>
<body>

<div class="container">

    <!-- Hero Header -->
    <div class="hero-header">
        <div class="hero-left">
            <h1>
                <i class="fas fa-chart-line"></i>
                Fleet Intelligence
                <span class="live-pulse">LIVE</span>
            </h1>
            <div class="subtitle">Real-time asset performance & predictive analytics</div>
            <div class="creator">Built by <strong>You</strong> — Fleet Intelligence Platform</div>
        </div>
        <div class="hero-right">
            <button class="hero-btn" onclick="document.getElementById('csvFile').click()"><i class="fas fa-upload"></i> Upload CSV</button>
            <button class="hero-btn primary" onclick="takeScreenshot()"><i class="fas fa-camera"></i> Screenshot</button>
            <button class="hero-btn primary" id="downloadPdfBtn"><i class="fas fa-file-pdf"></i> Report</button>
        </div>
    </div>

    <input type="file" id="csvFile" accept=".csv" style="display:none;">

    <!-- Upload Card -->
    <div class="upload-card" id="uploadCard">
        <h2>📊 Upload Your Fleet Data</h2>
        <p style="color:#64748b; margin-bottom:16px;">Upload a CSV file with your asset data</p>
        <div class="upload-button" id="uploadBtn">
            <i class="fas fa-file-csv" style="font-size:2rem;"></i><br>
            <strong>Choose File</strong><br>
            <small>or drag & drop</small>
        </div>
        <div id="fileStatus" style="margin-top:12px; color:#64748b;"></div>
    </div>

    <!-- Dashboard -->
    <div id="dashboard">

        <div id="dataTimestamp" style="background:#eef2ff; padding:6px 16px; border-radius:20px; display:inline-block; margin-bottom:20px;"></div>

        <!-- KPI Grid -->
        <div class="kpi-grid" id="kpiGrid">
            <div class="kpi-card"><div class="kpi-label">📊 Total Assets</div><div class="kpi-value" id="kpiTotal">0</div></div>
            <div class="kpi-card"><div class="kpi-label">🔴 Critical</div><div class="kpi-value" id="kpiCritical" style="color:#dc2626;">0</div></div>
            <div class="kpi-card"><div class="kpi-label">🟡 Warning</div><div class="kpi-value" id="kpiWarning" style="color:#f59e0b;">0</div></div>
            <div class="kpi-card"><div class="kpi-label">💸 Daily Loss</div><div class="kpi-value kpi-loss" id="kpiLoss">$0</div></div>
        </div>

        <!-- Filters -->
        <div class="filters">
            <div class="filter-group">
                <label>Region</label>
                <select id="regionFilter"><option value="all">All</option></select>
            </div>
            <div class="filter-group">
                <label>Status</label>
                <select id="statusFilter">
                    <option value="all">All</option>
                    <option value="critical">Critical</option>
                    <option value="warning">Warning</option>
                    <option value="good">Good</option>
                    <option value="offline">Offline</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Search</label>
                <input type="text" id="searchInput" placeholder="Search assets...">
            </div>
            <button id="resetBtn" class="reset-btn"><i class="fas fa-undo"></i> Reset</button>
        </div>

        <!-- Table -->
        <div class="table-wrapper">
            <table id="dataTable">
                <thead>
                    <tr>
                        <th>Asset</th>
                        <th>Address</th>
                        <th>City</th>
                        <th>Region</th>
                        <th>Status</th>
                        <th>Volume</th>
                        <th>Reject%</th>
                        <th>Uptime%</th>
                        <th>Est. Revenue</th>
                        <th>Daily Loss</th>
                        <th>Service Days</th>
                        <th>Call</th>
                    </tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>

        <!-- Map -->
        <div class="map-container">
            <h3><i class="fas fa-map-pin"></i> Asset Location Map</h3>
            <div id="map"></div>
            <div class="map-legend">
                <span><span class="map-legend-dot" style="background:#dc2626;"></span> Critical</span>
                <span><span class="map-legend-dot" style="background:#f59e0b;"></span> Warning</span>
                <span><span class="map-legend-dot" style="background:#10b981;"></span> Good</span>
                <span><span class="map-legend-dot" style="background:#6b7280;"></span> Offline</span>
            </div>
        </div>

    </div>

</div>

<div id="toast" class="toast"></div>

<script>
    // ============================================================
    // FLEET INTELLIGENCE DASHBOARD - GENERIC VERSION
    // ============================================================

    let allData = [];
    let currentSort = { column: 'loss', direction: 'desc' };
    let map = null;
    let lossChart = null;

    const TRANSACTION_VALUE = 5;

    // ===== HELPERS =====
    function showToast(msg) {
        let t = document.getElementById('toast');
        t.textContent = msg;
        t.style.display = 'block';
        setTimeout(() => t.style.display = 'none', 3000);
    }

    function getStatus(r) {
        let rej = parseFloat(r.Reject7Day) || 0;
        let uptime = parseFloat(r.Uptime7Day) || 100;
        if (r.KioskState === 'Offline' || uptime < 10) return 'Offline';
        if (rej >= 8) return 'Critical';
        if (rej >= 4) return 'Warning';
        return 'Good';
    }

    function getStatusBadge(r) {
        let s = getStatus(r);
        if (s === 'Critical') return '<span class="badge badge-critical">Critical</span>';
        if (s === 'Warning') return '<span class="badge badge-warning">Warning</span>';
        if (s === 'Offline') return '<span class="badge badge-offline">Offline</span>';
        return '<span class="badge badge-good">Good</span>';
    }

    function getVolume(r) { return parseFloat(r.Tx1Day) || 0; }

    function getReject(r) { return parseFloat(r.Reject7Day) || 0; }

    function getUptime(r) { return parseFloat(r.Uptime7Day) || 100; }

    function getEstRevenue(r) { return getVolume(r) * TRANSACTION_VALUE; }

    function calcLoss(r) {
        let vol = getVolume(r);
        let rej = getReject(r);
        let uptime = getUptime(r);
        return (vol * (rej / 100) * TRANSACTION_VALUE) + (vol * ((100 - uptime) / 100) * 4);
    }

    function getRegion(r) { return r.Province || r.State || 'Unknown'; }

    function getDaysSinceService(r) {
        let d = r.LastPM || '';
        if (!d || d === '—') return null;
        try {
            let parts = d.match(/(\d{2})\/(\d{2})\/(\d{2})/);
            if (parts) {
                let date = new Date(2000 + parseInt(parts[3]), parseInt(parts[1]) - 1, parseInt(parts[2]));
                return Math.ceil((new Date() - date) / 86400000);
            }
        } catch (e) {}
        return null;
    }

    function getPhoneNumber(r) { return r.Phone || r['Store Phone Number'] || ''; }

    function escapeHtml(s) { if (!s) return ''; return s.replace(/[&<>]/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' })[m]); }

    // ===== CSV PARSING =====
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
                else if (ch === ',' && !inQ) {
                    row[headers[col]] = cur.trim().replace(/"/g, '');
                    cur = '';
                    col++;
                } else cur += ch;
            }
            if (col < headers.length) row[headers[col]] = cur.trim().replace(/"/g, '');
            if (Object.keys(row).length) data.push(row);
        }
        if (!data.length) return false;
        allData = data.map(row => ({
            Store: row.Store || row['Store Name'] || 'Unknown',
            Address: row.Address || '',
            City: row.City || '',
            Province: row.State || row.Province || '',
            KioskState: row['Kiosk State'] || row.State || 'Attract',
            Tx1Day: row['1 Day TX'] || row.Volume || '0',
            Tx7Day: row['7 Day TX'] || '0',
            Reject7Day: row['7 Day Reject %'] || row.Reject7Day || '0',
            Uptime7Day: row['7 Day Uptime %'] || row.Uptime || '100',
            LastPM: row['Last PM Date'] || row['Last Service Date'] || '',
            Phone: row['Store Phone Number'] || row.Phone || '',
            Latitude: row.Latitude || '',
            Longitude: row.Longitude || ''
        }));
        return true;
    }

    // ===== FILTERS =====
    function filterData() {
        let f = [...allData];
        let region = document.getElementById('regionFilter')?.value || 'all';
        if (region !== 'all') f = f.filter(r => getRegion(r) === region);
        let status = document.getElementById('statusFilter')?.value || 'all';
        if (status !== 'all') f = f.filter(r => getStatus(r).toLowerCase() === status);
        let search = document.getElementById('searchInput')?.value.toLowerCase() || '';
        if (search) f = f.filter(r =>
            (r.Store || '').toLowerCase().includes(search) ||
            (r.City || '').toLowerCase().includes(search) ||
            (r.Address || '').toLowerCase().includes(search)
        );
        return f;
    }

    function sortData(d) {
        return [...d].sort((a, b) => {
            let va, vb;
            switch (currentSort.column) {
                case 'store': va = (a.Store || '').toLowerCase(); vb = (b.Store || '').toLowerCase(); break;
                case 'address': va = (a.Address || '').toLowerCase(); vb = (b.Address || '').toLowerCase(); break;
                case 'city': va = (a.City || '').toLowerCase(); vb = (b.City || '').toLowerCase(); break;
                case 'region': va = getRegion(a); vb = getRegion(b); break;
                case 'status': va = getStatus(a); vb = getStatus(b); break;
                case 'volume': va = getVolume(a); vb = getVolume(b); break;
                case 'reject': va = getReject(a); vb = getReject(b); break;
                case 'uptime': va = getUptime(a); vb = getUptime(b); break;
                case 'revenue': va = getEstRevenue(a); vb = getEstRevenue(b); break;
                case 'loss': va = calcLoss(a); vb = calcLoss(b); break;
                case 'serviceDays': va = getDaysSinceService(a) || 999; vb = getDaysSinceService(b) || 999; break;
                default: va = calcLoss(a); vb = calcLoss(b);
            }
            if (typeof va === 'number') return currentSort.direction === 'desc' ? vb - va : va - vb;
            return currentSort.direction === 'desc' ? String(vb).localeCompare(String(va)) : String(va).localeCompare(String(vb));
        });
    }

    // ===== RENDER =====
    function renderAll() {
        if (!allData.length) return;
        let f = filterData();
        f = sortData(f);

        const total = f.length;
        const crit = f.filter(r => getStatus(r) === 'Critical').length;
        const warn = f.filter(r => getStatus(r) === 'Warning').length;
        const offline = f.filter(r => getStatus(r) === 'Offline').length;
        const tLoss = f.reduce((s, r) => s + calcLoss(r), 0);

        document.getElementById('kpiTotal').textContent = total;
        document.getElementById('kpiCritical').textContent = crit;
        document.getElementById('kpiWarning').textContent = warn;
        document.getElementById('kpiLoss').textContent = '$' + tLoss.toFixed(0);

        const tbody = document.getElementById('tableBody');
        if (!f.length) { tbody.innerHTML = '<tr><td colspan="12">No assets found</td></tr>'; return; }

        tbody.innerHTML = f.map(r => {
            const name = r.Store || '—';
            const phone = getPhoneNumber(r);
            const callBtn = phone ? `<button class="call-btn" onclick="window.location.href='tel:${phone}'">📞</button>` : '—';
            const loss = calcLoss(r);
            const reject = getReject(r);
            const uptime = getUptime(r);
            const revenue = getEstRevenue(r);
            const status = getStatus(r);
            const serviceDays = getDaysSinceService(r);
            const rowClass = status === 'Critical' ? 'critical-row' : status === 'Warning' ? 'warning-row' : status === 'Offline' ? 'critical-row' : 'good-row';

            return `<tr class="${rowClass}">
                <td><strong>${escapeHtml(name)}</strong></td>
                <td>${escapeHtml(r.Address || '—')}</td>
                <td>${escapeHtml(r.City || '—')}</td>
                <td>${escapeHtml(getRegion(r))}</td>
                <td>${getStatusBadge(r)}</td>
                <td>${getVolume(r)}</td>
                <td style="color:${reject>=8?'#dc2626':reject>=4?'#f59e0b':'#10b981'};">${reject.toFixed(1)}%</td>
                <td style="color:${uptime<80?'#dc2626':uptime<95?'#f59e0b':'#10b981'};">${uptime.toFixed(1)}%</td>
                <td>$${revenue.toFixed(0)}</td>
                <td style="color:#dc2626;">$${loss.toFixed(0)}</td>
                <td>${serviceDays !== null ? serviceDays + 'd' : '—'}</td>
                <td>${callBtn}</td>
            </tr>`;
        }).join('');

        updateMap(f);
        populateFilters();
    }

    // ===== MAP =====
    function updateMap(data) {
        if (map) map.remove();
        map = L.map('map').setView([56.1304, -106.3468], 4);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { attribution: 'OSM' }).addTo(map);
        let bounds = [];
        data.forEach(r => {
            let lat = parseFloat(r.Latitude);
            let lng = parseFloat(r.Longitude);
            if (!isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0) {
                let s = getStatus(r);
                let color = s === 'Critical' ? '#dc2626' : s === 'Warning' ? '#f59e0b' : s === 'Offline' ? '#6b7280' : '#10b981';
                L.circleMarker([lat, lng], { radius: 8, fillColor: color, color: '#fff', weight: 2 })
                    .addTo(map)
                    .bindPopup(`<b>${escapeHtml(r.Store)}</b><br>Loss: $${calcLoss(r).toFixed(0)}`);
                bounds.push([lat, lng]);
            }
        });
        if (bounds.length) map.fitBounds(bounds);
        else map.fitBounds([[42, -79], [50, -60]]);
        setTimeout(() => map.invalidateSize(), 100);
    }

    // ===== FILTERS SETUP =====
    function populateFilters() {
        if (!allData.length) return;
        const regions = [...new Set(allData.map(r => getRegion(r)))].filter(r => r && r !== 'Unknown');
        const sel = document.getElementById('regionFilter');
        const current = sel.value;
        sel.innerHTML = '<option value="all">All</option>' + regions.sort().map(p => `<option value="${p}">${p}</option>`).join('');
        if ([...sel.options].some(o => o.value === current)) sel.value = current;
    }

    // ===== SCREENSHOT =====
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

    // ===== REPORT =====
    function downloadReport() {
        if (!allData.length) return showToast('No data');
        showToast('Generating report...');
        html2canvas(document.getElementById('dashboard'), { scale: 2, backgroundColor: '#f4f6fc' }).then(canvas => {
            let link = document.createElement('a');
            link.download = 'fleet_report_' + Date.now() + '.png';
            link.href = canvas.toDataURL();
            link.click();
            showToast('Report saved');
        }).catch(() => showToast('Failed'));
    }

    // ===== SORTING =====
    function setupSorting() {
        document.querySelectorAll('#dataTable th').forEach(th => {
            const key = th.textContent.trim().toLowerCase();
            const map = {
                'asset': 'store', 'address': 'address', 'city': 'city', 'region': 'region',
                'status': 'status', 'volume': 'volume', 'reject%': 'reject', 'uptime%': 'uptime',
                'est. revenue': 'revenue', 'daily loss': 'loss', 'service days': 'serviceDays'
            };
            const sortKey = map[key] || null;
            if (!sortKey) return;
            th.style.cursor = 'pointer';
            th.title = 'Click to sort';
            th.addEventListener('click', () => {
                if (currentSort.column === sortKey) currentSort.direction = currentSort.direction === 'desc' ? 'asc' : 'desc';
                else { currentSort.column = sortKey; currentSort.direction = 'desc'; }
                renderAll();
            });
        });
    }

    // ===== EVENT LISTENERS =====
    document.getElementById('uploadBtn').addEventListener('click', () => document.getElementById('csvFile').click());

    document.getElementById('csvFile').addEventListener('change', function(e) {
        if (!e.target.files || !e.target.files[0]) return;
        const file = e.target.files[0];
        document.getElementById('fileStatus').textContent = 'Loading: ' + file.name;
        if (!file.name.endsWith('.csv')) { showToast('Please upload a CSV file'); return; }
        const reader = new FileReader();
        reader.onload = function(ev) {
            if (parseCSV(ev.target.result)) {
                document.getElementById('uploadCard').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                document.getElementById('dataTimestamp').textContent = '📅 ' + new Date().toLocaleString() + ' — ' + allData.length + ' assets';
                populateFilters();
                setupSorting();
                renderAll();
                showToast('Loaded ' + allData.length + ' assets');
            } else showToast('Invalid CSV format');
        };
        reader.readAsText(file);
    });

    document.getElementById('resetBtn').addEventListener('click', () => {
        document.getElementById('regionFilter').value = 'all';
        document.getElementById('statusFilter').value = 'all';
        document.getElementById('searchInput').value = '';
        renderAll();
    });

    document.getElementById('searchInput').addEventListener('input', renderAll);
    document.getElementById('regionFilter').addEventListener('change', renderAll);
    document.getElementById('statusFilter').addEventListener('change', renderAll);
    document.getElementById('downloadPdfBtn').addEventListener('click', downloadReport);

    // Load Leaflet
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    document.head.appendChild(script);

    console.log('Fleet Intelligence Dashboard loaded');
</script>

</body>
</html>
"""


@app.route('/')
def home():
    return HTML_TEMPLATE


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
