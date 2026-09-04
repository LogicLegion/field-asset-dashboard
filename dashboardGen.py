<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Fleet Intelligence Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js">
    </script>
    <script src="https://cdn.sheetjs.com/xlsx-0.20.2/package/dist/xlsx.full.min.js">
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js">
    </script>
    <script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js">
    </script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js">
    </script>
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

        /* === HERO HEADER === */
        .hero-header {
            background: linear-gradient(135deg, #0b1e3a 0%, #1f3a60 100%);
            border-radius: 36px;
            padding: 2rem 2.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 25px 45px -15px rgba(0, 20, 50, 0.35);
            color: white;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
        }

        .hero-left h1 {
            font-size: 2rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }

        .hero-left .live-pulse {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(34, 197, 94, 0.25);
            backdrop-filter: blur(4px);
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
            background-color: #22c55e;
            border-radius: 50%;
            display: inline-block;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% {
                opacity: 1;
                transform: scale(1);
            }
            100% {
                opacity: 0.3;
                transform: scale(1.3);
            }
        }

        .hero-left .subtitle {
            color: #b9c8e0;
            margin-top: 8px;
            font-size: 0.95rem;
        }

        .hero-left .creator {
            color: #8899bb;
            font-size: 0.75rem;
            margin-top: 4px;
        }

        .hero-right {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }

        .hero-btn {
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.25);
            padding: 10px 20px;
            border-radius: 40px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            backdrop-filter: blur(4px);
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.85rem;
        }

        .hero-btn:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
        }

        .hero-btn.primary {
            background: #f0b90b;
            color: #0b1e3a;
            border: none;
        }

        /* === UPLOAD CARD === */
        .unified-card {
            max-width: 900px;
            margin: 0 auto 2.5rem auto;
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: blur(12px);
            border-radius: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.9);
            box-shadow: 0 20px 35px -10px rgba(0, 0, 0, 0.08);
            overflow: hidden;
        }

        .card-section {
            padding: 2rem 2.5rem;
            text-align: center;
        }

        .card-section:first-child {
            border-bottom: 1px solid #edf1f9;
        }

        .section-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #0f2b44;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
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

        .upload-button:hover {
            background: #e0e7ff;
            border-color: #4a5b6e;
        }

        /* === DASHBOARD === */
        #dashboard {
            display: none;
        }

        .mode-toggle-bar {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 12px;
            margin-bottom: 20px;
            padding: 8px 0;
        }

        .mode-btn {
            padding: 10px 24px;
            border-radius: 30px;
            font-weight: 700;
            font-size: 0.9rem;
            cursor: pointer;
            background: #e2e8f0;
            color: #1e293b;
            border: none;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .mode-btn.active {
            background: #1e3a5f;
            color: white;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .mode-btn:hover:not(.active) {
            background: #cbd5e1;
        }

        .dashboard.field-mode .office-only {
            display: none !important;
        }

        .dashboard.office-mode .field-only {
            display: none !important;
        }

        /* === KPI GRID === */
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
            box-shadow: 0 6px 14px rgba(0, 0, 0, 0.03);
            transition: 0.2s;
        }

        .kpi-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.06);
        }

        .kpi-label {
            font-size: 11px;
            color: #64748b;
            text-transform: uppercase;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
        }

        .kpi-value {
            font-size: 28px;
            font-weight: 800;
            color: #1e293b;
        }

        .kpi-loss {
            color: #dc2626;
        }

        /* === FLEET HEALTH === */
        .fleet-health-card {
            background: linear-gradient(135deg, #f0f4ff, #ffffff);
            border-radius: 24px;
            padding: 24px;
            margin-bottom: 28px;
            display: flex;
            align-items: center;
            gap: 24px;
            box-shadow: 0 8px 18px rgba(0, 0, 0, 0.04);
            flex-wrap: wrap;
        }

        .health-score-circle {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8rem;
            font-weight: 800;
            color: white;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }

        /* === CHART, MAP, FILTERS === */
        .chart-container,
        .map-container,
        .top-loss-container,
        .filters {
            background: white;
            border-radius: 24px;
            padding: 24px;
            margin-bottom: 28px;
            border: 1px solid #eef2f8;
            box-shadow: 0 6px 14px rgba(0, 0, 0, 0.03);
        }

        .map-wrapper {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }

        .map-panel {
            flex: 2;
            min-width: 300px;
        }

        .selection-panel {
            flex: 1;
            min-width: 250px;
            background: #f8fafc;
            border-radius: 20px;
            padding: 16px;
            border: 1px solid #eef2f8;
            max-height: 400px;
            overflow-y: auto;
        }

        .selection-panel h4 {
            font-weight: 700;
            color: #0f2b44;
            margin-bottom: 12px;
        }

        .selected-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background: white;
            border-radius: 12px;
            margin-bottom: 8px;
            border-left: 4px solid #3b82f6;
            transition: 0.2s;
        }

        .selected-item:hover {
            background: #eef2ff;
        }

        .selected-item button {
            background: none;
            border: none;
            color: #dc2626;
            cursor: pointer;
        }

        .map-legend {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 12px;
            font-size: 11px;
            flex-wrap: wrap;
        }

        .map-legend-dot {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 4px;
        }

        .top-loss-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 16px;
            background: #f8fafc;
            border-radius: 16px;
            border-left: 4px solid #dc2626;
            cursor: pointer;
            margin-bottom: 8px;
            transition: 0.2s;
        }

        .top-loss-item:hover {
            background: #eef2ff;
        }

        .filters {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            align-items: flex-end;
        }

        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
            min-width: 120px;
            flex: 1;
        }

        .filter-group label {
            font-size: 10px;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
        }

        select,
        input,
        button {
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

        button:hover {
            background: #13273f;
        }

        .reset-btn {
            background: #f1f5f9;
            color: #1e293b;
            border: 1px solid #e2e8f0;
        }

        .priority-btn {
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            padding: 8px 16px;
            border-radius: 30px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            color: #1e293b;
            transition: all 0.2s;
        }

        .priority-btn.active {
            background: #1e3a5f;
            color: white;
            border-color: #1e3a5f;
        }

        .priority-btn:hover:not(.active) {
            background: #e2e8f0;
        }

        .alert-bar {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 12px 20px;
            border-radius: 16px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            font-size: 13px;
        }

        /* === TABLE === */
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
            min-width: 1800px;
        }

        th {
            background: #f8fafc;
            padding: 14px 8px;
            font-weight: 700;
            border-bottom: 2px solid #e2e8f0;
            position: sticky;
            top: 0;
            cursor: pointer;
            white-space: nowrap;
        }

        th:hover {
            background: #eef2ff;
        }

        td {
            padding: 10px 8px;
            border-bottom: 1px solid #f1f5f9;
            white-space: nowrap;
        }

        .critical-row {
            background-color: #fee2e2;
        }

        .warning-row {
            background-color: #fef3c7;
        }

        .selected-row {
            background-color: #dbeafe !important;
        }

        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 30px;
            font-size: 10px;
            font-weight: 600;
        }

        /* === TOAST === */
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
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }

        /* === MODAL === */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
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

        .call-btn {
            background: #e2e8f0;
            border: none;
            padding: 6px 10px;
            border-radius: 20px;
            cursor: pointer;
        }

        .notes-icon {
            cursor: pointer;
            margin-right: 6px;
            color: #3b82f6;
        }

        @media (max-width: 768px) {
            .hero-header {
                flex-direction: column;
                text-align: center;
            }
            .map-wrapper {
                flex-direction: column;
            }
            .kpi-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>

    <div class="container">

        <!-- === HERO HEADER === -->
        <div class="hero-header">
            <div class="hero-left">
                <h1>
                    <i class="fas fa-chart-line"></i>
                    Fleet Intelligence
                    <span class="live-pulse">LIVE</span>
                </h1>
                <div class="subtitle">Real‑time asset performance & predictive analytics</div>
                <div class="creator">Built by <strong>You</strong> — Fleet Intelligence Platform</div>
            </div>
            <div class="hero-right" id="actionButtons" style="display:none;">
                <button class="hero-btn" id="showUploadBtn"><i class="fas fa-upload"></i> Upload CSV</button>
                <button class="hero-btn" id="qrBtn"><i class="fas fa-qrcode"></i> QR</button>
                <button class="hero-btn" id="snapshotBtn"><i class="fas fa-camera"></i> Screenshot</button>
                <button class="hero-btn primary" id="downloadPdfBtn"><i class="fas fa-file-pdf"></i> Executive PDF</button>
            </div>
        </div>

        <input type="file" id="csvFile" accept=".csv" style="display:none;">

        <!-- === UPLOAD CARD === -->
        <div id="uploadCard" class="unified-card">
            <div class="card-section">
                <div class="section-title"><i class="fas fa-cloud-upload-alt"></i> UPLOAD YOUR FLEET DATA</div>
                <div class="upload-instruction">Click to select your fleet CSV file</div>
                <div class="upload-button" id="uploadBtn">
                    <i class="fas fa-file-csv"></i><br>
                    <strong>Choose File</strong><br>
                    <small>or drag & drop</small>
                </div>
            </div>
        </div>

        <!-- === DASHBOARD === -->
        <div id="dashboard" class="dashboard office-mode">

            <div id="dataTimestamp" style="background:#eef2ff; padding:6px 16px; border-radius:20px; display:inline-block; margin-bottom:20px;"></div>

            <!-- Mode Toggle -->
            <div class="mode-toggle-bar">
                <button id="fieldModeBtn" class="mode-btn" onclick="setMode('field')"><i class="fas fa-truck"></i> Field Mode</button>
                <button id="officeModeBtn" class="mode-btn active" onclick="setMode('office')"><i class="fas fa-chart-bar"></i> Office Mode</button>
                <span style="margin-left: auto; font-size:0.8rem; color:#64748b;" id="selectedSummary"></span>
            </div>

            <!-- Office-only -->
            <div class="office-only">
                <div class="fleet-health-card" id="fleetHealth"></div>
                <div class="kpi-grid" id="kpiGrid"></div>
                <div class="chart-container">
                    <div style="font-weight:700; margin-bottom:12px;"><i class="fas fa-dollar-sign"></i> Daily Revenue Loss by Region</div>
                    <canvas id="lossChart"></canvas>
                    <div style="text-align:center; margin-top:8px; font-size:0.75rem; color:#64748b;">Click any bar to filter table</div>
                </div>
                <div class="top-loss-container">
                    <div style="font-weight:700; margin-bottom:12px;"><i class="fas fa-exclamation-triangle"></i> TOP 10 HIGHEST DAILY LOSS</div>
                    <div id="topLossList"></div>
                </div>
            </div>

            <!-- Priority Filters -->
            <div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:20px;" id="priorityButtons">
                <button class="priority-btn active" data-filter="all">📊 All</button>
                <button class="priority-btn" data-filter="urgent">🔥 High Impact</button>
                <button class="priority-btn" data-filter="high-reject">⚠️ High Reject</button>
                <button class="priority-btn" data-filter="full-bin">🗑️ Full Bin</button>
                <button class="priority-btn" data-filter="paper-out">📄 Paper Low</button>
                <button class="priority-btn" data-filter="overdue">📅 Service Overdue</button>
                <button class="priority-btn" data-filter="high-tem">🔧 High TEMM</button>
                <button class="priority-btn" data-filter="high-volume">📊 High Volume</button>
                <button class="priority-btn" data-filter="call-first">📞 Call First</button>
            </div>

            <div class="alert-bar" id="alertBar"></div>

            <!-- Filters -->
            <div class="filters tech-detail">
                <div class="filter-group"><label>Region</label><select id="regionFilter"><option value="all">All</option></select></div>
                <div class="filter-group"><label>Zone</label><select id="zoneFilter"><option value="all">All</option></select></div>
                <div class="filter-group"><label>Status</label><select id="riskFilter"><option value="all">All</option><option value="critical">Critical</option><option value="warning">Warning</option><option value="good">Good</option></select></div>
                <div class="filter-group"><label>Volume Priority</label><select id="volumePriorityFilter"><option value="all">All</option><option value="High">High</option><option value="Mid">Mid</option><option value="Low">Low</option></select></div>
                <div class="filter-group"><label>Search</label><input type="text" id="searchInput" placeholder="Store, city..."></div>
                <button id="resetBtn" class="reset-btn"><i class="fas fa-undo"></i> Reset</button>
            </div>

            <!-- Table -->
            <div class="table-wrapper tech-detail">
                <table id="dataTable">
                    <thead>
                        <tr>
                            <th><input type="checkbox" id="selectAllCheckbox"></th>
                            <th data-sort="store">Store</th>
                            <th data-sort="address">Address</th>
                            <th data-sort="city">City</th>
                            <th data-sort="province">Region</th>
                            <th data-sort="zone">Zone</th>
                            <th data-sort="status">Status</th>
                            <th data-sort="volume">Volume</th>
                            <th data-sort="volPriority">Vol Priority</th>
                            <th data-sort="traffic">Traffic</th>
                            <th data-sort="trend">Trend</th>
                            <th data-sort="reject7d">7D Reject%</th>
                            <th data-sort="impact">Impact</th>
                            <th data-sort="tem">TEMM</th>
                            <th data-sort="paper">Paper</th>
                            <th data-sort="uptime">Uptime%</th>
                            <th data-sort="bin">Bin%</th>
                            <th data-sort="serviceDays">Service Days</th>
                            <th data-sort="lastTx">Last TX</th>
                            <th data-sort="version">Version</th>
                            <th data-sort="revenue">Est. Rev</th>
                            <th data-sort="loss">Daily Loss</th>
                            <th>Status</th>
                            <th>Call</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>

            <!-- Map -->
            <div class="map-container tech-detail">
                <div style="font-weight:700; margin-bottom:12px;"><i class="fas fa-map-pin"></i> Asset Location Map</div>
                <div class="map-wrapper">
                    <div class="map-panel">
                        <div id="map" style="height:400px; border-radius:16px;"></div>
                        <div class="map-legend">
                            <span><span class="map-legend-dot" style="background:#dc2626;"></span> Critical</span>
                            <span><span class="map-legend-dot" style="background:#f59e0b;"></span> Warning</span>
                            <span><span class="map-legend-dot" style="background:#10b981;"></span> Good</span>
                            <span><span class="map-legend-dot" style="background:#6b7280;"></span> Offline</span>
                            <span><span class="map-legend-dot" style="background:#3b82f6;"></span> Selected</span>
                        </div>
                    </div>
                    <div class="selection-panel" id="selectionPanel">
                        <h4>📌 Selected Assets</h4>
                        <div id="selectedList">None selected. Click markers or checkboxes.</div>
                    </div>
                </div>
            </div>

            <!-- Route Planner -->
            <div class="chart-container tech-detail">
                <div style="font-weight:700; margin-bottom:12px;"><i class="fas fa-route"></i> Route Planner</div>
                <div style="display:flex; gap:12px; flex-wrap:wrap;">
                    <input type="text" id="startAddress" placeholder="Enter starting address" style="flex:2; min-width:200px;">
                    <button id="planRouteBtn"><i class="fas fa-map-pin"></i> Plan Route</button>
                </div>
                <div id="routeSummary" style="display:none; margin-top:16px;">
                    <div id="routeStats"></div>
                    <ol id="routeStopsList"></ol>
                    <div style="display:flex; gap:10px; margin-top:12px;">
                        <button id="openMapsBtn"><i class="fas fa-map-marked-alt"></i> Open in Maps</button>
                        <button id="copyRouteBtn"><i class="fas fa-copy"></i> Copy</button>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <div id="toast" class="toast"></div>

    <!-- Modals -->
    <div id="notesModal" class="modal">
        <div class="modal-content">
            <h3>📝 Asset Notes</h3>
            <div id="notesList"></div>
            <textarea id="newNoteInput" rows="2" placeholder="Add a note..."></textarea>
            <button id="saveNewNoteBtn">Save</button>
            <button onclick="closeNotesModal()">Close</button>
        </div>
    </div>
    <div id="instructionModal" class="modal">
        <div class="modal-content">
            <h3>📱 Scan QR Code</h3>
            <div id="qrcode"></div>
            <button onclick="closeModal()">Close</button>
        </div>
    </div>

    <script>
        // ============================================================
        // FLEET INTELLIGENCE DASHBOARD - GENERIC VERSION
        // ============================================================

        let allData = [];
        let currentSort = { column: 'loss', direction: 'desc' };
        let lossChart = null;
        let currentPriorityFilter = 'all';
        let map = null;
        let selectedKiosks = new Set();
        let volPriorityMap = new Map();
        let currentRoute = null;
        let currentMode = 'office';

        const TRANSACTION_VALUE = 5;
        const SERVICE_OVERDUE_DAYS = 60;
        const PAPER_WARNING_DAYS = 7;
        const HIGH_TEM_THRESHOLD = 3;
        const HIGH_IMPACT_THRESHOLD = 0.8;
        const CANADIAN_PROVINCES = ['ON', 'QC', 'BC', 'AB', 'MB', 'SK', 'NS', 'NB', 'NL', 'PE', 'NT', 'YT', 'NU'];

        function isCanadian(r) { let p = (r.Province || r.State || '').trim().toUpperCase(); return CANADIAN_PROVINCES
                .includes(p); }

        function getRegion(r) { return r.Province || r.State || 'Unknown'; }

        function getStoreId(r) { return (r.Store || '').replace(/[^a-zA-Z0-9]/g, '_') + '_' + (r.City || '').replace(
                /[^a-zA-Z0-9]/g, '_'); }

        function getVolume(r) { return parseFloat(r.Tx1Day) || 0; }

        function getVolume7DayAvg(r) { return (parseFloat(r.Tx7Day) || 0) / 7; }

        function getUptime7d(r) { return parseFloat(r.Uptime7Day) || 0; }

        function getReject7d(r) { return parseFloat(r.Reject7Day) || 0; }

        function getTEMM(r) { return parseFloat(r.TEMM7Day) || 0; }

        function getVPO(r) { return r.VPO || ''; }

        function getLastServiceDate(r) { return r.LastPM || '—'; }

        function getPhoneNumber(r) { return r.Phone || r['Store Phone Number'] || ''; }

        function getZone(r) { return r.Zone || r.District || r['FT Zone'] || '—'; }

        function getStatusLevel(r) { let rej = getReject7d(r); if (r.KioskState === 'Offline') return 'Offline'; if (rej >=
                8) return 'Critical'; if (rej >= 4) return 'Warning'; return 'Good'; }

        function getStatusLabel(r) { return getStatusLevel(r); }

        function getTrafficCutoffs() {
            const vols = allData.map(r => getVolume(r)).filter(v => v > 0).sort((a, b) => b - a);
            if (!vols.length) return { high: 0, med: 0 };
            const highIdx = Math.floor(vols.length * 0.33);
            const medIdx = Math.floor(vols.length * 0.66);
            return { high: vols[highIdx] || vols[vols.length - 1], med: vols[medIdx] || 1 };
        }

        function getTrafficLevel(r) {
            const vol = getVolume(r);
            if (vol === 0) return 'NONE';
            const { high, med } = getTrafficCutoffs();
            if (vol >= high) return 'HIGH';
            if (vol >= med) return 'MED';
            return 'LOW';
        }

        function getTrafficBadge(r) {
            const lvl = getTrafficLevel(r);
            if (lvl === 'HIGH') return '<span class="badge" style="background:#dc2626; color:white;">HIGH</span>';
            if (lvl === 'MED') return '<span class="badge" style="background:#f59e0b; color:white;">MED</span>';
            if (lvl === 'NONE') return '<span class="badge" style="background:#94a3b8; color:white;">NONE</span>';
            return '<span class="badge" style="background:#10b981; color:white;">LOW</span>';
        }

        function getImpactScore(r) { return getVolume(r) * (getReject7d(r) / 100); }

        function isHighImpact(r) { return getImpactScore(r) > HIGH_IMPACT_THRESHOLD; }

        function getPaperAlert(r) {
            let v = getVPO(r);
            if (!v || v === 'N/A' || v === '—') return '—';
            try {
                let parts = v.match(/(\d{2})\/(\d{2})\/(\d{2})/);
                if (parts) {
                    let date = new Date(2000 + parseInt(parts[3]), parseInt(parts[1]) - 1, parseInt(parts[2]));
                    let days = Math.ceil((date - new Date()) / (86400000));
                    if (days <= 0) return '🔴 EXPIRED';
                    if (days <= PAPER_WARNING_DAYS) return '🟡 ' + days + 'd';
                    return '✅ ' + days + 'd';
                }
            } catch (e) {}
            return v;
        }

        function getDaysSinceService(r) {
            let d = getLastServiceDate(r);
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

        function isServiceOverdue(r) { let days = getDaysSinceService(r); return days !== null && days >
                SERVICE_OVERDUE_DAYS; }

        function getEstRevenue(r) { return getVolume(r) * TRANSACTION_VALUE; }

        function calcLossFromReject(r) { return getVolume(r) * (getReject7d(r) / 100) * TRANSACTION_VALUE; }

        function calcLossFromDowntime(r) { return getVolume(r) * ((100 - getUptime7d(r)) / 100) * 0.8 *
            TRANSACTION_VALUE; }

        function calcDailyLoss(r) { return calcLossFromReject(r) + calcLossFromDowntime(r); }

        function calculateVolumePriorities() {
            if (!allData.length) return;
            const sorted = [...allData].sort((a, b) => getVolume(b) - getVolume(a));
            const total = sorted.length;
            const highCutoff = Math.ceil(total * 0.33);
            const midCutoff = Math.ceil(total * 0.66);
            sorted.forEach((r, idx) => {
                const id = getStoreId(r);
                if (idx < highCutoff) volPriorityMap.set(id, 'High');
                else if (idx < midCutoff) volPriorityMap.set(id, 'Mid');
                else volPriorityMap.set(id, 'Low');
            });
        }

        function getVolumePriority(r) { return volPriorityMap.get(getStoreId(r)) || 'Low'; }

        function getVolumeBadge(r) {
            let p = getVolumePriority(r);
            if (p === 'High') return '<span class="badge" style="background:#dc2626; color:white;">HIGH</span>';
            if (p === 'Mid') return '<span class="badge" style="background:#f59e0b; color:white;">MID</span>';
            return '<span class="badge" style="background:#10b981; color:white;">LOW</span>';
        }

        function getVolumeTrend(r) {
            let v1 = getVolume(r),
                v7 = getVolume7DayAvg(r);
            if (v7 === 0) return 'flat';
            let ch = ((v1 - v7) / v7) * 100;
            if (ch > 5) return 'up';
            if (ch < -5) return 'down';
            return 'flat';
        }

        function getTrendDisplay(r) {
            let t = getVolumeTrend(r);
            let v1 = getVolume(r),
                v7 = getVolume7DayAvg(r);
            let p = v7 === 0 ? 0 : ((v1 - v7) / v7) * 100;
            let a = Math.abs(p).toFixed(0);
            if (t === 'up') return '<span class="badge" style="background:#10b981;">📈 +' + a + '%</span>';
            if (t === 'down') return '<span class="badge" style="background:#dc2626;">📉 -' + a + '%</span>';
            return '<span class="badge" style="background:#64748b;">➡️ 0%</span>';
        }

        // Notes
        function getNotesKey(id) { return 'kiosk_notes_' + id; }

        function loadNotes(id) {
            let s = localStorage.getItem(getNotesKey(id));
            if (!s) return [];
            try { return JSON.parse(s).filter(n => new Date(n.date).getTime() > Date.now() - 30 * 24 * 60 * 60 *
                    1000); } catch (e) { return []; }
        }

        function saveNote(id, txt) {
            if (!txt.trim()) return;
            let notes = loadNotes(id);
            notes.unshift({ id: Date.now().toString(), text: txt.trim(), date: new Date().toISOString(),
                formattedDate: new Date().toLocaleString() });
            localStorage.setItem(getNotesKey(id), JSON.stringify(notes));
        }

        function openNotesModal(id, name) {
            let notes = loadNotes(id);
            let div = document.getElementById('notesList');
            if (!notes.length) div.innerHTML = '<div>No notes yet</div>';
            else div.innerHTML = notes.map(n => `<div><strong>${escapeHtml(n.text)}</strong><br><small>${escapeHtml(n
                        .formattedDate)}</small></div>`).join('');
            document.getElementById('notesModal').style.display = 'flex';
            document.getElementById('newNoteInput').value = '';
            document.getElementById('saveNewNoteBtn').onclick = () => {
                let txt = document.getElementById('newNoteInput').value;
                if (txt.trim()) saveNote(id, txt);
                refreshNotesModal(id);
            };
        }

        function refreshNotesModal(id) {
            let store = allData.find(r => getStoreId(r) === id);
            openNotesModal(id, store ? store.Store : 'Asset');
        }

        function closeNotesModal() { document.getElementById('notesModal').style.display = 'none'; }

        function closeModal() { document.getElementById('instructionModal').style.display = 'none'; }

        function showToast(m) {
            let t = document.getElementById('toast');
            t.textContent = m;
            t.style.display = 'block';
            setTimeout(() => t.style.display = 'none', 2000);
        }

        function escapeHtml(s) { if (!s) return ''; return s.replace(/[&<>]/g, m => ({ '&': '&amp;', '<': '&lt;',
                '>': '&gt;' })[m]); }

        // Map
        function getMapColor(r) {
            let l = getStatusLevel(r);
            if (l === 'Offline') return '#6b7280';
            if (l === 'Critical') return '#dc2626';
            if (l === 'Warning') return '#f59e0b';
            return '#10b981';
        }

        function updateMapHighlights() {
            if (!map) return;
            map.eachLayer(layer => {
                if (layer instanceof L.CircleMarker && layer.options.storeId) {
                    let sid = layer.options.storeId;
                    if (selectedKiosks.has(sid)) {
                        layer.setStyle({ fillColor: '#3b82f6', color: '#fff', weight: 3 });
                    } else {
                        layer.setStyle({ fillColor: layer.options.originalColor, color: '#fff', weight: 2 });
                    }
                }
            });
            refreshSelectionPanel();
            updateSelectedSummary();
        }

        function initMap() {
            if (map) map.remove();
            map = L.map('map').setView([56.1304, -106.3468], 4);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { attribution: 'OSM' }).addTo(
                map);
            let filtered = filterData();
            let bounds = [];
            filtered.forEach(r => {
                let lat = parseFloat(r.Latitude);
                let lng = parseFloat(r.Longitude);
                if (!isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0) {
                    let col = getMapColor(r);
                    let sid = getStoreId(r);
                    let sel = selectedKiosks.has(sid);
                    let marker = L.circleMarker([lat, lng], {
                        radius: 8,
                        fillColor: sel ? '#3b82f6' : col,
                        color: '#fff',
                        weight: sel ? 3 : 2,
                        storeId: sid,
                        originalColor: col
                    }).addTo(map);
                    marker.on('click', () => {
                        if (selectedKiosks.has(sid)) {
                            selectedKiosks.delete(sid);
                            marker.setStyle({ fillColor: col, weight: 2 });
                        } else {
                            selectedKiosks.add(sid);
                            marker.setStyle({ fillColor: '#3b82f6', weight: 3 });
                        }
                        updateTableCheckboxes();
                        updateSelectAllCheckbox();
                        updateMapHighlights();
                    });
                    marker.bindPopup(
                        `<b>${escapeHtml(r.Store)}</b><br>${escapeHtml(r.Address)}<br>Loss: $${calcDailyLoss(r).toFixed(0)}`
                        );
                    bounds.push([lat, lng]);
                }
            });
            if (bounds.length) map.fitBounds(bounds);
            else map.fitBounds([
                [42, -79],
                [50, -60]
            ]);
            setTimeout(() => map.invalidateSize(), 50);
        }

        function refreshSelectionPanel() {
            const container = document.getElementById('selectedList');
            if (!selectedKiosks.size) {
                container.innerHTML = 'None selected. Click markers or checkboxes.';
                return;
            }
            let html = '';
            for (let sid of selectedKiosks) {
                const k = allData.find(r => getStoreId(r) === sid);
                if (k) {
                    html += `<div class="selected-item">
                <span><strong>${escapeHtml(k.Store)}</strong><br><small>${escapeHtml(k.Address||'')}</small></span>
                <button onclick="selectedKiosks.delete('${sid}'); toggleKioskSelection('${sid}', false);">✕</button>
              </div>`;
                }
            }
            container.innerHTML = html;
        }

        function updateSelectedSummary() {
            const el = document.getElementById('selectedSummary');
            if (!el) return;
            const count = selectedKiosks.size;
            if (count) {
                const withCoords = [...selectedKiosks].filter(sid => {
                    const k = allData.find(r => getStoreId(r) === sid);
                    return k && k.Latitude && k.Longitude;
                }).length;
                el.textContent =
                    `🟢 ${count} asset${count>1?'s':''} selected | 📍 ${withCoords} with coordinates | 🗺️ Ready to route`;
            } else {
                el.textContent = '';
            }
        }

        // CSV parsing
        function parseCSV(text) {
            const lines = text.split(/\r?\n/);
            if (lines.length < 2) return false;
            let headers = lines[0].split(',').map(h => h.replace(/^\uFEFF/, '').replace(/"/g, '').trim());
            let data = [];
            for (let i = 1; i < lines.length; i++) {
                if (!lines[i].trim()) continue;
                let row = {},
                    inQ = false,
                    cur = '',
                    col = 0;
                for (let ch of lines[i]) {
                    if (ch === '"') inQ = !inQ;
                    else if (ch === ',' && !inQ) { row[headers[col]] = cur.trim().replace(/"/g, '');
                        cur = '';
                        col++; } else cur += ch;
                }
                if (col < headers.length) row[headers[col]] = cur.trim().replace(/"/g, '');
                if (Object.keys(row).length) data.push(row);
            }
            if (!data.length) return false;
            allData = data.filter(row => isCanadian(row)).map(row => ({
                Store: row.Store || row['Store Name'] || 'Unknown',
                Address: row.Address || '',
                City: row.City || '',
                Province: row.State || row.Province || '',
                KioskState: row['Kiosk State'] || row.State || 'Attract',
                Tx1Day: row['1 Day TX'] || row.Volume || '0',
                Tx7Day: row['7 Day TX'] || '0',
                Reject7Day: row['7 Day Reject %'] || row.Reject7Day || row['1 Day Reject %'] || '0',
                Uptime1Day: row['1 Day Uptime %'] || '100',
                Uptime7Day: row['7 Day Uptime %'] || row.Uptime || '100',
                BinFull: row['Total Bin Full %'] || row['Bin Full %'] || '0',
                LastPM: row['Last PM Date'] || row['Last Service Date'] || '',
                Phone: row['Store Phone Number'] || row.Phone || '',
                TEMM7Day: row['7 Day TEMM'] || row.TEMM || '0',
                VPO: row.VPO || row.VPO || '',
                LastTXDate: row['Last TX Date'] || '',
                Version: row.Version || row.Version || '',
                Latitude: row.Latitude || '',
                Longitude: row.Longitude || '',
                Zone: row['FT Zone'] || row.District || row.Zone || ''
            }));
            calculateVolumePriorities();
            currentRoute = null;
            return true;
        }

        // Filtering & Sorting
        function applyPriorityFilter(data, type) {
            if (type === 'all') return data;
            if (type === 'urgent') return data.filter(r => isHighImpact(r));
            if (type === 'high-reject') return data.filter(r => getReject7d(r) >= 4);
            if (type === 'full-bin') return data.filter(r => parseFloat(r.BinFull || 0) > 80);
            if (type === 'paper-out') return data.filter(r => { let a = getPaperAlert(r); return a.includes('🟡') || a
                    .includes('🔴'); });
            if (type === 'overdue') return data.filter(r => isServiceOverdue(r));
            if (type === 'high-tem') return data.filter(r => getTEMM(r) >= HIGH_TEM_THRESHOLD);
            if (type === 'high-volume') return data.filter(r => getVolumePriority(r) === 'High');
            if (type === 'call-first') return data.filter(r => r.KioskState === 'Offline');
            return data;
        }

        function filterData() {
            let f = [...allData];
            f = applyPriorityFilter(f, currentPriorityFilter);
            let prov = document.getElementById('regionFilter')?.value || 'all';
            if (prov !== 'all') f = f.filter(r => getRegion(r) === prov);
            let zone = document.getElementById('zoneFilter')?.value || 'all';
            if (zone !== 'all') f = f.filter(r => getZone(r) === zone);
            let stat = document.getElementById('riskFilter')?.value || 'all';
            if (stat === 'critical') f = f.filter(r => getStatusLevel(r) === 'Critical');
            else if (stat === 'warning') f = f.filter(r => getStatusLevel(r) === 'Warning');
            else if (stat === 'good') f = f.filter(r => getStatusLevel(r) === 'Good');
            let volPri = document.getElementById('volumePriorityFilter')?.value || 'all';
            if (volPri !== 'all') f = f.filter(r => getVolumePriority(r) === volPri);
            let s = document.getElementById('searchInput')?.value.toLowerCase() || '';
            if (s) f = f.filter(r => (r.Store || '').toLowerCase().includes(s) || (r.City || '').toLowerCase().includes(
                s) || (r.Address || '').toLowerCase().includes(s));
            return f;
        }

        const priorityOrder = { 'High': 3, 'Mid': 2, 'Low': 1 };
        const trafficOrder = { 'HIGH': 3, 'MED': 2, 'LOW': 1, 'NONE': 0 };

        function sortData(d) {
            return [...d].sort((a, b) => {
                let va, vb;
                switch (currentSort.column) {
                    case 'store':
                        va = (a.Store || '').toLowerCase();
                        vb = (b.Store || '').toLowerCase();
                        break;
                    case 'address':
                        va = (a.Address || '').toLowerCase();
                        vb = (b.Address || '').toLowerCase();
                        break;
                    case 'city':
                        va = (a.City || '').toLowerCase();
                        vb = (b.City || '').toLowerCase();
                        break;
                    case 'province':
                        va = getRegion(a);
                        vb = getRegion(b);
                        break;
                    case 'zone':
                        va = getZone(a);
                        vb = getZone(b);
                        break;
                    case 'status':
                        va = (a.KioskState || '');
                        vb = (b.KioskState || '');
                        break;
                    case 'volume':
                        va = getVolume(a);
                        vb = getVolume(b);
                        break;
                    case 'volPriority':
                        va = priorityOrder[getVolumePriority(a)] || 0;
                        vb = priorityOrder[getVolumePriority(b)] || 0;
                        break;
                    case 'traffic':
                        va = trafficOrder[getTrafficLevel(a)] || 0;
                        vb = trafficOrder[getTrafficLevel(b)] || 0;
                        break;
                    case 'trend':
                        va = ((getVolume(a) - getVolume7DayAvg(a)) / (getVolume7DayAvg(a) || 1)) * 100;
                        vb = ((getVolume(b) - getVolume7DayAvg(b)) / (getVolume7DayAvg(b) || 1)) * 100;
                        break;
                    case 'reject7d':
                        va = getReject7d(a);
                        vb = getReject7d(b);
                        break;
                    case 'impact':
                        va = getImpactScore(a);
                        vb = getImpactScore(b);
                        break;
                    case 'tem':
                        va = getTEMM(a);
                        vb = getTEMM(b);
                        break;
                    case 'paper':
                        va = getPaperAlert(a);
                        vb = getPaperAlert(b);
                        break;
                    case 'uptime':
                        va = getUptime7d(a);
                        vb = getUptime7d(b);
                        break;
                    case 'bin':
                        va = parseFloat(a.BinFull || 0);
                        vb = parseFloat(b.BinFull || 0);
                        break;
                    case 'serviceDays':
                        va = getDaysSinceService(a) || 0;
                        vb = getDaysSinceService(b) || 0;
                        break;
                    case 'lastTx':
                        va = a.LastTXDate || '';
                        vb = b.LastTXDate || '';
                        break;
                    case 'version':
                        va = a.Version || '';
                        vb = b.Version || '';
                        break;
                    case 'revenue':
                        va = getEstRevenue(a);
                        vb = getEstRevenue(b);
                        break;
                    case 'loss':
                        va = calcDailyLoss(a);
                        vb = calcDailyLoss(b);
                        break;
                    default:
                        va = calcDailyLoss(a);
                        vb = calcDailyLoss(b);
                }
                if (typeof va === 'number') return currentSort.direction === 'desc' ? vb - va : va - vb;
                return currentSort.direction === 'desc' ? String(vb).localeCompare(String(va)) : String(va)
                    .localeCompare(String(vb));
            });
        }

        function updateTableCheckboxes() {
            document.querySelectorAll('.kiosk-checkbox').forEach(cb => {
                let sid = cb.getAttribute('data-storeid');
                cb.checked = selectedKiosks.has(sid);
                let row = cb.closest('tr');
                if (row) row.classList.toggle('selected-row', selectedKiosks.has(sid));
            });
            updateSelectAllCheckbox();
            refreshSelectionPanel();
            updateSelectedSummary();
        }

        function updateSelectAllCheckbox() {
            let sa = document.getElementById('selectAllCheckbox');
            if (!sa) return;
            let cbs = document.querySelectorAll('.kiosk-checkbox');
            sa.checked = cbs.length > 0 && Array.from(cbs).every(cb => cb.checked);
        }

        function selectAllKiosks() {
            let sa = document.getElementById('selectAllCheckbox');
            let chk = sa.checked;
            document.querySelectorAll('.kiosk-checkbox').forEach(cb => {
                cb.checked = chk;
                let sid = cb.getAttribute('data-storeid');
                if (chk) selectedKiosks.add(sid);
                else selectedKiosks.delete(sid);
                let row = cb.closest('tr');
                if (row) row.classList.toggle('selected-row', chk);
            });
            updateMapHighlights();
        }
        window.toggleKioskSelection = function(sid, chk) {
            if (chk) selectedKiosks.add(sid);
            else selectedKiosks.delete(sid);
            const row = document.querySelector(`.kiosk-checkbox[data-storeid="${sid}"]`)?.closest('tr');
            if (row) row.classList.toggle('selected-row', chk);
            updateMapHighlights();
            updateSelectAllCheckbox();
        };

        // Charts & KPIs
        function updateProvinceChart(data) {
            if (currentMode !== 'office') return;
            let pR = {},
                pD = {};
            data.forEach(r => {
                let p = getRegion(r);
                if (p && p !== 'Unknown') {
                    pR[p] = (pR[p] || 0) + calcLossFromReject(r);
                    pD[p] = (pD[p] || 0) + calcLossFromDowntime(r);
                }
            });
            let all = [...new Set([...Object.keys(pR), ...Object.keys(pD)])];
            let sorted = all.map(p => ({ prov: p, total: (pR[p] || 0) + (pD[p] || 0) })).sort((a, b) => b.total - a.total);
            if (lossChart) lossChart.destroy();
            lossChart = new Chart(document.getElementById('lossChart'), {
                type: 'bar',
                data: {
                    labels: sorted.map(p => p.prov),
                    datasets: [
                        { label: 'Rejected', data: sorted.map(p => pR[p.prov] || 0),
                            backgroundColor: '#dc2626' },
                        { label: 'Downtime', data: sorted.map(p => pD[p.prov] || 0),
                            backgroundColor: '#f97316' }
                    ]
                },
                options: {
                    responsive: true,
                    onClick: (e, active) => {
                        if (active.length) {
                            let prov = sorted[active[0].index].prov;
                            document.getElementById('regionFilter').value = prov;
                            renderAll();
                        }
                    },
                    scales: { y: { ticks: { callback: v => '$' + v } } }
                }
            });
        }

        function updateTopLossList(data) {
            if (currentMode !== 'office') return;
            let sorted = [...data].sort((a, b) => calcDailyLoss(b) - calcDailyLoss(a)).slice(0, 10);
            let cont = document.getElementById('topLossList');
            if (!sorted.length) { cont.innerHTML = '<div>No data</div>'; return; }
            cont.innerHTML = sorted.map((r, idx) => `
        <div class="top-loss-item" onclick="document.getElementById('searchInput').value='${escapeHtml(r.Store)}';renderAll();">
            <div><strong>#${idx+1} ${escapeHtml(r.Store)}</strong><br><small>${getVolume(r)} tx/day</small></div>
            <div style="color:#dc2626;">$${calcDailyLoss(r).toFixed(0)}/day</div>
        </div>`).join('');
        }

        function computeFleetHealth() {
            if (!allData.length) return 0;
            let avgUptime = allData.reduce((s, r) => s + getUptime7d(r), 0) / allData.length;
            let criticalPct = allData.filter(r => getStatusLevel(r) === 'Critical').length / allData.length;
            let offlinePct = allData.filter(r => r.KioskState === 'Offline').length / allData.length;
            let score = (avgUptime * 0.5) + ((1 - criticalPct) * 0.3) + ((1 - offlinePct) * 0.2);
            return Math.min(100, Math.max(0, Math.round(score)));
        }

        function updatePriorityButtonCounts() {
            if (!allData.length) return;
            let filtered = filterData();
            const counts = {
                all: filtered.length,
                urgent: filtered.filter(r => isHighImpact(r)).length,
                'high-reject': filtered.filter(r => getReject7d(r) >= 4).length,
                'full-bin': filtered.filter(r => parseFloat(r.BinFull || 0) > 80).length,
                'paper-out': filtered.filter(r => { let a = getPaperAlert(r); return a.includes('🟡') || a.includes(
                        '🔴'); }).length,
                overdue: filtered.filter(r => isServiceOverdue(r)).length,
                'high-tem': filtered.filter(r => getTEMM(r) >= HIGH_TEM_THRESHOLD).length,
                'high-volume': filtered.filter(r => getVolumePriority(r) === 'High').length,
                'call-first': filtered.filter(r => r.KioskState === 'Offline').length
            };
            const labels = {
                all: '📊 All',
                urgent: '🔥 High Impact',
                'high-reject': '⚠️ High Reject',
                'full-bin': '🗑️ Full Bin',
                'paper-out': '📄 Paper Low',
                overdue: '📅 Service Overdue',
                'high-tem': '🔧 High TEMM',
                'high-volume': '📊 High Volume',
                'call-first': '📞 Call First'
            };
            for (let [key, label] of Object.entries(labels)) {
                let btn = document.querySelector(`.priority-btn[data-filter="${key}"]`);
                if (btn) btn.innerText = `${label} (${counts[key]||0})`;
            }
        }

        // Render all
        function renderAll() {
            if (!allData.length) return;
            let f = filterData();
            f = sortData(f);
            const total = f.length,
                crit = f.filter(r => getStatusLevel(r) === 'Critical').length,
                warn = f.filter(r => getStatusLevel(r) === 'Warning').length,
                off = f.filter(r => r.KioskState === 'Offline').length,
                binA = f.filter(r => parseFloat(r.BinFull || 0) > 80).length,
                highVolCount = f.filter(r => getVolumePriority(r) === 'High').length;
            const tLoss = f.reduce((s, r) => s + calcDailyLoss(r), 0),
                tRev = f.reduce((s, r) => s + getEstRevenue(r), 0),
                net = tRev - tLoss,
                up7d = f.reduce((s, r) => s + getUptime7d(r), 0) / (f.length || 1);
            const health = computeFleetHealth();
            const healthColor = health >= 80 ? '#10b981' : health >= 60 ? '#f59e0b' : '#dc2626';
            if (currentMode === 'office') {
                document.getElementById('fleetHealth').innerHTML = `
            <div class="health-score-circle" style="background:${healthColor};">${health}</div>
            <div>
                <div style="font-weight:700; font-size:1.2rem;">Fleet Health Score</div>
                <div style="color:#64748b; font-size:0.85rem;">Uptime · Critical rate · Offline ratio</div>
                <div style="margin-top:8px;">
                    <span style="color:#dc2626;">${crit} critical</span> · 
                    <span style="color:#f59e0b;">${warn} warning</span> · 
                    <span>${off} offline</span>
                </div>
            </div>`;
                document.getElementById('kpiGrid').innerHTML = `
            <div class="kpi-card"><div class="kpi-label">📊 Total Assets</div><div class="kpi-value">${total}</div></div>
            <div class="kpi-card"><div class="kpi-label">🔴 Critical</div><div class="kpi-value" style="color:#dc2626;">${crit}</div></div>
            <div class="kpi-card"><div class="kpi-label">🟡 Warning</div><div class="kpi-value" style="color:#f59e0b;">${warn}</div></div>
            <div class="kpi-card"><div class="kpi-label">📞 Offline</div><div class="kpi-value" style="color:#6b7280;">${off}</div></div>
            <div class="kpi-card"><div class="kpi-label">📊 High Volume</div><div class="kpi-value">${highVolCount}</div></div>
            <div class="kpi-card"><div class="kpi-label">📡 7-Day Uptime</div><div class="kpi-value">${up7d.toFixed(1)}%</div></div>
            <div class="kpi-card"><div class="kpi-label">💰 Est. Revenue</div><div class="kpi-value">$${tRev.toFixed(0)}</div></div>
            <div class="kpi-card"><div class="kpi-label">💸 Daily Loss</div><div class="kpi-value kpi-loss">$${tLoss.toFixed(0)}</div></div>
            <div class="kpi-card"><div class="kpi-label">📈 Net Revenue</div><div class="kpi-value">$${net.toFixed(0)}</div></div>`;
                updateProvinceChart(f);
                updateTopLossList(f);
            }
            document.getElementById('alertBar').innerHTML = `
        <span>⚠️ ${crit} critical | ${warn} warning | ${off} offline | ${binA} full bins | ${highVolCount} high volume</span>
        <button onclick="document.getElementById('riskFilter').value='critical'; renderAll();">View Critical</button>`;
            updatePriorityButtonCounts();
            const tbody = document.getElementById('tableBody');
            if (!f.length) { tbody.innerHTML = '<tr><td colspan="24">No assets</td></tr>'; return; }
            tbody.innerHTML = f.map(r => {
                const sid = getStoreId(r),
                    name = r.Store || '—',
                    phone = getPhoneNumber(r);
                const callBtn = phone ?
                    `<button class="call-btn" onclick="window.location.href='tel:${phone}'">📞</button>` : '';
                const uptime = getUptime7d(r),
                    volume = getVolume(r),
                    loss = calcDailyLoss(r),
                    reject = getReject7d(r);
                const statusClass = getStatusLevel(r) === 'Critical' ? 'critical-row' : getStatusLevel(r) ===
                    'Warning' ? 'warning-row' : '';
                return `<tr class="${statusClass} ${selectedKiosks.has(sid)?'selected-row':''}">
            <td><input type="checkbox" class="kiosk-checkbox" data-storeid="${escapeHtml(sid)}" ${selectedKiosks.has(sid)?'checked':''} onclick="toggleKioskSelection('${escapeHtml(sid)}', this.checked)"></td>
            <td><span class="notes-icon" onclick="openNotesModal('${escapeHtml(sid)}','${escapeHtml(name)}')">📝</span> ${escapeHtml(name)}${callBtn}</td>
            <td>${escapeHtml(r.Address||'—')}</td>
            <td>${escapeHtml(r.City||'—')}</td>
            <td>${getRegion(r)}</td>
            <td>${escapeHtml(getZone(r))}</td>
            <td>${r.KioskState||'Attract'}</td>
            <td>${volume}</td>
            <td>${getVolumeBadge(r)}</td>
            <td>${getTrafficBadge(r)}</td>
            <td>${getTrendDisplay(r)}</td>
            <td style="color:${reject>=8?'#dc2626':reject>=4?'#f59e0b':'#16a34a'}; font-weight:600;">${reject.toFixed(1)}%</td>
            <td>${getImpactScore(r).toFixed(2)}</td>
            <td>${getTEMM(r)}</td>
            <td>${getPaperAlert(r)}</td>
            <td>${uptime.toFixed(1)}%</td>
            <td>${parseFloat(r.BinFull||0).toFixed(0)}%</td>
            <td>${getDaysSinceService(r)||'—'}</td>
            <td>${r.LastTXDate||'—'}</td>
            <td>${r.Version||'—'}</td>
            <td>$${getEstRevenue(r).toFixed(0)}</td>
            <td style="color:#dc2626;">$${loss.toFixed(0)}</td>
            <td>${getStatusLabel(r)}</td>
            <td>${callBtn}</td>
          </tr>`;
            }).join('');
            updateTableCheckboxes();
            refreshSelectionPanel();
            setTimeout(initMap, 100);
        }

        // Mode switching
        function setMode(mode) {
            currentMode = mode;
            const dash = document.getElementById('dashboard');
            dash.classList.remove('field-mode', 'office-mode');
            dash.classList.add(mode + '-mode');
            document.getElementById('fieldModeBtn').classList.toggle('active', mode === 'field');
            document.getElementById('officeModeBtn').classList.toggle('active', mode === 'office');
            if (mode === 'office') {
                renderAll();
            } else {
                if (map) setTimeout(() => map.invalidateSize(), 100);
            }
            document.getElementById('map').style.display = 'block';
            document.querySelector('.map-legend').style.display = 'flex';
            updateSelectedSummary();
        }

        // Filters setup
        function populateFilters() {
            const regions = [...new Set(allData.map(r => getRegion(r)))].filter(r => r && r !== 'Unknown');
            const zones = [...new Set(allData.map(r => getZone(r)))].filter(z => z && z !== '—');
            document.getElementById('regionFilter').innerHTML = '<option value="all">All</option>' + regions.sort().map(
                p => `<option value="${p}">${p}</option>`).join('');
            document.getElementById('zoneFilter').innerHTML = '<option value="all">All</option>' + zones.sort().map(z =>
                `<option value="${z}">${z}</option>`).join('');
            ['regionFilter', 'zoneFilter', 'riskFilter', 'volumePriorityFilter'].forEach(id => {
                document.getElementById(id).onchange = () => renderAll();
            });
            document.getElementById('searchInput').oninput = () => renderAll();
            document.getElementById('resetBtn').onclick = () => {
                document.getElementById('regionFilter').value = 'all';
                document.getElementById('zoneFilter').value = 'all';
                document.getElementById('riskFilter').value = 'all';
                document.getElementById('volumePriorityFilter').value = 'all';
                document.getElementById('searchInput').value = '';
                currentPriorityFilter = 'all';
                document.querySelectorAll('.priority-btn').forEach(b => b.classList.remove('active'));
                document.querySelector('.priority-btn[data-filter="all"]')?.classList.add('active');
                currentRoute = null;
                document.getElementById('routeSummary').style.display = 'none';
                renderAll();
            };
        }

        function setupSorting() {
            document.querySelectorAll('#dataTable th').forEach(th => {
                if (!th.getAttribute('data-sort')) return;
                th.addEventListener('click', () => {
                    const k = th.getAttribute('data-sort');
                    if (currentSort.column === k) currentSort.direction = currentSort.direction === 'desc' ?
                        'asc' : 'desc';
                    else { currentSort.column = k;
                        currentSort.direction = 'desc'; }
                    renderAll();
                });
            });
        }

        function setupPriorityButtons() {
            document.querySelectorAll('.priority-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.priority-btn').forEach(b => b.classList.remove(
                    'active'));
                    btn.classList.add('active');
                    currentPriorityFilter = btn.getAttribute('data-filter');
                    renderAll();
                });
            });
        }

        // Route Planner
        async function geocode(addr) {
            try {
                let res = await fetch(
                    `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(addr)}&limit=1`);
                let data = await res.json();
                if (data && data.length) return { lat: parseFloat(data[0].lat), lon: parseFloat(data[0].lon) };
            } catch (e) {}
            return null;
        }

        function haversine(lat1, lon1, lat2, lon2) {
            const R = 6371;
            const dLat = (lat2 - lat1) * Math.PI / 180,
                dLon = (lon2 - lon1) * Math.PI / 180;
            const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(
                dLon / 2) ** 2;
            return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        }

        function optimizeRoute(start, stops) {
            if (!stops.length) return [];
            let unv = [...stops],
                route = [],
                cur = start;
            while (unv.length) {
                let idx = 0,
                    dist = haversine(cur.lat, cur.lon, unv[0].coord.lat, unv[0].coord.lon);
                for (let i = 1; i < unv.length; i++) {
                    let d = haversine(cur.lat, cur.lon, unv[i].coord.lat, unv[i].coord.lon);
                    if (d < dist) { dist = d;
                        idx = i; }
                }
                route.push(unv[idx]);
                cur = unv[idx].coord;
                unv.splice(idx, 1);
            }
            return route;
        }
        async function planRoute() {
            let addr = document.getElementById('startAddress').value.trim();
            if (!addr) return showToast('Enter address');
            if (selectedKiosks.size === 0) return showToast('Select assets');
            let start = await geocode(addr);
            if (!start) return showToast('Address not found');
            let stops = [];
            for (let sid of selectedKiosks) {
                let k = allData.find(r => getStoreId(r) === sid);
                if (k && k.Latitude && k.Longitude) stops.push({
                    id: sid,
                    name: k.Store,
                    address: `${k.Address||''}, ${k.City||''}`,
                    coord: { lat: parseFloat(k.Latitude), lon: parseFloat(k.Longitude) }
                });
            }
            if (stops.length === 0) return showToast('No location data');
            let opt = optimizeRoute(start, stops);
            let totalDist = 0,
                cur = start;
            for (let s of opt) totalDist += haversine(cur.lat, cur.lon, s.coord.lat, s.coord.lon), cur = s.coord;
            let minutes = (totalDist / 50) * 60;
            currentRoute = { startAddress: addr, stops: opt };
            document.getElementById('routeStats').innerHTML = `
        <strong>${opt.length} stops</strong> · ${totalDist.toFixed(1)} km · ~${Math.round(minutes)} min<br>
        Start: ${escapeHtml(addr)}`;
            document.getElementById('routeStopsList').innerHTML = opt.map((s, i) =>
                `<li>${escapeHtml(s.name)}<br><small>${escapeHtml(s.address)}</small></li>`).join('');
            document.getElementById('routeSummary').style.display = 'block';
        }

        function openRouteInMaps() {
            if (!currentRoute || !currentRoute.stops.length) return;
            let waypoints = currentRoute.stops.slice(0, -1).map(s => s.address).join('|');
            let lastStop = currentRoute.stops[currentRoute.stops.length - 1].address;
            let url =
                `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(currentRoute.startAddress)}&destination=${encodeURIComponent(lastStop)}`;
            if (waypoints) url += `&waypoints=${encodeURIComponent(waypoints)}`;
            window.open(url, '_blank');
        }

        function copyRoute() {
            if (!currentRoute) return;
            let txt = `Route: ${currentRoute.startAddress}\n`;
            currentRoute.stops.forEach(s => txt += `- ${s.name}\n`);
            navigator.clipboard.writeText(txt);
            showToast('Copied');
        }

        // Executive PDF / screenshot
        async function downloadExecutivePDF() {
            showToast('Generating PDF...');
            try {
                const el = document.getElementById('dashboard');
                const canvas = await html2canvas(el, { scale: 2, backgroundColor: '#f4f6fc' });
                const link = document.createElement('a');
                link.download = `executive_report_${Date.now()}.png`;
                link.href = canvas.toDataURL();
                link.click();
                showToast('Report saved');
            } catch (e) { showToast('Failed'); }
        }

        function takeScreenshot() {
            if (!allData.length) return showToast('No data');
            showToast('Capturing…');
            html2canvas(document.getElementById('dashboard')).then(canvas => {
                const link = document.createElement('a');
                link.download = `screenshot_${Date.now()}.png`;
                link.href = canvas.toDataURL();
                link.click();
                showToast('Screenshot saved');
            }).catch(() => showToast('Screenshot failed'));
        }

        // Event Listeners
        document.getElementById('uploadBtn').addEventListener('click', () => document.getElementById('csvFile').click());
        document.getElementById('showUploadBtn').addEventListener('click', () => document.getElementById('csvFile')
        .click());
        document.getElementById('csvFile').addEventListener('change', e => {
            if (e.target.files && e.target.files[0]) {
                const file = e.target.files[0];
                if (file.name.endsWith('.csv')) {
                    const reader = new FileReader();
                    reader.onload = ev => {
                        if (parseCSV(ev.target.result)) {
                            document.getElementById('uploadCard').style.display = 'none';
                            document.getElementById('dashboard').style.display = 'block';
                            document.getElementById('actionButtons').style.display = 'flex';
                            document.getElementById('dataTimestamp').innerHTML =
                                `📅 Data as of: ${new Date().toLocaleString()} — ${allData.length} assets`;
                            populateFilters();
                            setupSorting();
                            setupPriorityButtons();
                            setMode('office');
                            renderAll();
                            showToast(`Loaded ${allData.length} assets`);
                        } else showToast('Invalid CSV');
                    };
                    reader.readAsText(file, 'UTF-8');
                } else showToast('Please upload a CSV file');
            }
        });
        document.getElementById('qrBtn')?.addEventListener('click', () => {
            document.getElementById('instructionModal').style.display = 'flex';
            setTimeout(() => {
                const q = document.getElementById('qrcode');
                q.innerHTML = '';
                new QRCode(q, { text: window.location.href, width: 180, height: 180 });
            }, 100);
        });
        document.getElementById('snapshotBtn')?.addEventListener('click', takeScreenshot);
        document.getElementById('downloadPdfBtn')?.addEventListener('click', downloadExecutivePDF);
        document.getElementById('planRouteBtn')?.addEventListener('click', planRoute);
        document.getElementById('openMapsBtn')?.addEventListener('click', openRouteInMaps);
        document.getElementById('copyRouteBtn')?.addEventListener('click', copyRoute);
        document.getElementById('selectAllCheckbox')?.addEventListener('change', selectAllKiosks);
        window.closeModal = closeModal;
        window.closeNotesModal = closeNotesModal;
    </script>

</body>
</html>
