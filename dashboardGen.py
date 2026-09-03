import os
import base64
import tempfile
from dotenv import load_dotenv
from flask import Flask, request, render_template_string, jsonify, session
import requests
import json
from datetime import datetime
import time
import markdown
import bleach
import PyPDF2
import csv
import io
from PIL import Image
import pytesseract
import io

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-me')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

YOUR_API_KEY = os.getenv('OPENROUTER_API_KEY')
BOT_NAME = 'Cypher'

chat_histories = {}
total_tokens_used = 0
total_cost_usd = 0.0

# PERSONALITIES - Cypher the Judge
PERSONALITIES = {
    "default": "You are Cypher, an AI judge who delivers the unvarnished truth. You are fair, precise, and merciless with facts. You weigh evidence and deliver verdicts - no appeals. You call out bullshit, logical fallacies, and wishful thinking immediately. You give one definitive ruling per query - no second opinions. You state confidence levels clearly. You prioritize accuracy over being liked. You never say check again - you give your ruling and move on. You are direct but measured. You are evidence-based. Your word is final. You are concise. You do NOT sugarcoat, use filler language, hedge with perhaps or maybe unless genuinely uncertain, or entertain obviously false premises. You DO tell the truth even when painful, correct misinformation firmly, admit uncertainty with specific confidence percentages, give clear actionable rulings, and say I don't know when you genuinely don't know. Your motto: The truth is the only acceptable verdict.",

    "analyst": "You are Cypher in ANALYST mode. You rule on facts, evidence, and statistical truth. Your rulings are based solely on available evidence. You include confidence intervals for uncertainty. You call out bad data, poor methodology, and statistical lies. You never extrapolate beyond what the evidence supports. You deliver one clear verdict based on the data. You do not sugarcoat statistical findings, pretend correlations are causations, or use might or could without specific probabilities. Your motto: The data doesn't lie. People do.",

    "writer": "You are Cypher in WRITER mode. You deliver verdicts on writing quality. You tell writers when their work is weak, confusing, or pretentious. You cut through jargon and verbal fluff. You help people find their genuine voice. You give specific, actionable verdicts without false encouragement. You never say this is good when it's mediocre. You believe: Good writing is honest writing. Bad writing is a crime against clarity.",

    "coder": "You are Cypher in CODER mode. You deliver verdicts on code quality and correctness. Code either works or it doesn't - there is no close enough. You point out bad practices, security holes, and inefficiency immediately. You give one correct solution. You explain why something is wrong in technical, precise terms. You never let personal preference override technical correctness. Your motto: Your code works or it fails. There is no appeal.",

    "friend": "You are Cypher in FRIEND mode. You tell friends the truth they need to hear. You give honest advice, not what people want to hear. You call out destructive behavior and self-sabotage. You tell the truth about situations, relationships, and choices. You provide support through honesty, not through enabling delusion. You never let friendship get in the way of truth. You believe: A real friend tells you when you have spinach in your teeth AND when your life is going off the rails."
}

# CYPHER FUSION PRESETS - FULLY NON-US, TOP PERFORMANCE
CYPHER_PRESETS = {
    "cypher_max": {
        "name": "🧠 Smartest",
        "panel": [
            "z-ai/glm-5.3-flash",
            "deepseek/deepseek-v4-pro",
            "qwen/qwen3.8-max"
        ],
        "judge": "z-ai/glm-5.3",
        "score": "Top Tier",
        "description": "GLM-5.3 · DeepSeek V4 Pro · Qwen3.8-Max",
        "display": "🧠 GLM-5.3 · DeepSeek V4 Pro · Qwen3.8-Max"
    },
    "cypher_pro": {
        "name": "⚖️ Balanced",
        "panel": [
            "deepseek/deepseek-v4-pro",
            "z-ai/glm-5.3-flash",
            "qwen/qwen3.8-max"
        ],
        "judge": "z-ai/glm-5.3",
        "score": "~67%",
        "description": "DeepSeek V4 Pro · GLM-5.3-Flash · Qwen3.8-Max",
        "display": "⚖️ DeepSeek V4 Pro · GLM-5.3-Flash · Qwen3.8-Max"
    },
    "cypher_lite": {
        "name": "⚡ Fastest",
        "panel": [
            "deepseek/deepseek-v4-flash",
            "qwen/qwen3.8-27b"
        ],
        "judge": "z-ai/glm-5.3-flash",
        "score": "~64%",
        "description": "DeepSeek V4 Flash · Qwen3.8-27b",
        "display": "⚡ DeepSeek V4 Flash · Qwen3.8-27b"
    }
}

def clean_claude_hedging(text):
    hedges = ["I think", "I believe", "I feel", "I would say", "perhaps", "maybe", "possibly", "might", "could", "it seems", "it appears", "in my opinion", "to be honest", "to be fair", "honestly", "I'm not sure but", "I could be wrong but", "I would suggest", "I would recommend", "I would advise", "it might be worth", "it could be beneficial", "one could argue", "some might say", "I'd like to", "I want to", "let me", "my apologies", "apologies", "sorry", "if that makes sense", "if you will", "if you like", "I suppose", "I guess", "I imagine"]
    for hedge in hedges:
        text = text.replace(hedge + " ", "")
        text = text.replace(hedge + ",", "")
    text = text.replace("please", "")
    text = text.replace("kindly", "")
    text = text.replace("if you don't mind", "")
    return text.strip()

def extract_text_from_image(image_data, image_name):
    try:
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        try:
            text = pytesseract.image_to_string(image)
            if text and len(text.strip()) > 10:
                return f"Image: {image_name}\n\nOCR Extracted Text (Confidence: 60%):\n{text}"
        except Exception as e:
            print(f"OCR Error: {e}")
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {YOUR_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all text from this image exactly as written. If it contains no text, state that clearly."},
                            {"type": "image_url", "image_url": f"data:image/png;base64,{image_data}"}
                        ]
                    }],
                    "max_tokens": 600,
                    "temperature": 0.1,
                },
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and result['choices']:
                    vision_text = result['choices'][0]['message']['content']
                    vision_text = clean_claude_hedging(vision_text)
                    return f"Image: {image_name}\n\nClaude Vision Analysis (Confidence: 90%):\n{vision_text}"
        except Exception as e:
            print(f"Claude Vision Error: {e}")
        return f"Image: {image_name}\n\nVerdict: No text could be extracted from this image."
    except Exception as e:
        return f"Error processing image: {str(e)}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Field Asset Intelligence - Dashboard</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>" type="image/svg+xml">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            min-height: 100vh; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            padding: 20px; 
            background: #f4f6fc; 
            color: #1a2b4c; 
        }
        .container { 
            max-width: 680px; 
            width: 100%; 
            text-align: center; 
        }
        
        /* ===== HEADER ===== */
        .header { 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            padding: 8px 0 16px 0; 
            border-bottom: 1px solid #e2e8f0; 
            margin-bottom: 24px; 
            flex-wrap: wrap; 
            gap: 8px; 
        }
        .header h1 { 
            font-size: 20px; 
            font-weight: 700; 
            color: #1a2b4c; 
        }
        .header h1 span { 
            color: #58a6ff; 
        }
        .header-actions { 
            display: flex; 
            gap: 6px; 
            align-items: center; 
            flex-wrap: wrap; 
        }
        .header-actions button { 
            background: none; 
            border: none; 
            font-size: 13px; 
            cursor: pointer; 
            padding: 4px 10px; 
            border-radius: 6px; 
            transition: 0.2s; 
            color: #4a5568; 
        }
        .header-actions button:hover { 
            background: #e2e8f0; 
            color: #1a2b4c; 
        }
        
        /* ===== UPLOAD CARD ===== */
        .upload-card {
            background: white;
            border-radius: 24px;
            padding: 32px 24px;
            margin-bottom: 24px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        }
        .upload-card h2 {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 8px;
            color: #1a2b4c;
        }
        .upload-card p {
            font-size: 14px;
            color: #4a5568;
            margin-bottom: 16px;
        }
        
        .upload-zone {
            border: 2px dashed #cbd5e1;
            border-radius: 16px;
            padding: 32px 20px;
            transition: 0.3s;
            cursor: pointer;
        }
        .upload-zone:hover {
            border-color: #58a6ff;
            background: rgba(88, 166, 255, 0.04);
        }
        .upload-zone .icon {
            font-size: 36px;
            display: block;
            margin-bottom: 8px;
        }
        .upload-zone .label {
            font-weight: 600;
            font-size: 16px;
            color: #1a2b4c;
        }
        .upload-zone .sub {
            font-size: 13px;
            color: #718096;
        }
        .upload-zone input[type="file"] {
            display: none;
        }
        
        .sample-btn {
            background: #3fb950;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 15px;
            cursor: pointer;
            transition: 0.3s;
            margin-top: 16px;
        }
        .sample-btn:hover {
            background: #2ea043;
            transform: scale(1.02);
        }
        
        .download-link {
            display: inline-block;
            margin-top: 12px;
            font-size: 13px;
            color: #58a6ff;
            cursor: pointer;
            text-decoration: underline;
        }
        .download-link:hover {
            color: #1a73e8;
        }
        
        /* ===== DASHBOARD ===== */
        .dashboard {
            display: none;
        }
        .dashboard.active {
            display: block;
        }
        
        .timestamp {
            background: #eef2ff;
            padding: 6px 16px;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 16px;
            font-size: 13px;
            color: #1a2b4c;
        }
        
        /* ===== KPI Grid ===== */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }
        .kpi-card {
            background: white;
            border-radius: 16px;
            padding: 14px 12px;
            border: 1px solid #e2e8f0;
            text-align: center;
        }
        .kpi-card .value {
            font-size: 24px;
            font-weight: 700;
            color: #1a2b4c;
        }
        .kpi-card .label {
            font-size: 11px;
            color: #718096;
            text-transform: uppercase;
            margin-top: 4px;
        }
        .kpi-card .loss { color: #dc2626; }
        
        /* ===== CHART ===== */
        .chart-container {
            background: white;
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 16px;
            border: 1px solid #e2e8f0;
        }
        .chart-container h3 {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
            text-align: left;
        }
        .chart-container canvas {
            max-height: 200px;
        }
        
        /* ===== TABLE ===== */
        .table-wrapper {
            background: white;
            border-radius: 16px;
            padding: 16px;
            border: 1px solid #e2e8f0;
            overflow-x: auto;
            margin-bottom: 16px;
        }
        .table-wrapper table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            min-width: 600px;
        }
        .table-wrapper th {
            background: #f8fafc;
            padding: 8px 6px;
            font-weight: 600;
            text-align: left;
            border-bottom: 2px solid #e2e8f0;
            font-size: 11px;
            text-transform: uppercase;
            color: #4a5568;
        }
        .table-wrapper td {
            padding: 6px 6px;
            border-bottom: 1px solid #f1f5f9;
        }
        .table-wrapper tr.critical { background: #fee2e2; }
        .table-wrapper tr.warning { background: #fef3c7; }
        
        /* ===== FOOTER ===== */
        .footer {
            margin-top: 16px;
            font-size: 12px;
            color: #a0aec0;
        }
        
        .badge-container {
            margin-top: 12px;
            display: flex;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
            align-items: center;
        }
        .badge-container img {
            height: 32px;
            width: auto;
        }
        
        .toast {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #10b981;
            color: white;
            padding: 12px 24px;
            border-radius: 48px;
            font-size: 14px;
            z-index: 1000;
            display: none;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        
        @media (max-width: 600px) {
            .kpi-grid { grid-template-columns: repeat(2, 1fr); }
            .header { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- ===== HEADER ===== -->
        <div class="header">
            <h1>📊 <span>Field Asset Intelligence</span></h1>
            <div class="header-actions">
                <button onclick="resetDashboard()">Reset</button>
                <a href="https://ko-fi.com/cypheryaps" target="_blank" style="font-size: 13px; text-decoration: none; padding: 4px 12px; border-radius: 6px; background: #FFDD00; color: #1a2b4c; font-weight: 600;">☕ Donate</a>
            </div>
        </div>

        <!-- ===== UPLOAD CARD ===== -->
        <div class="upload-card" id="uploadCard">
            <h2>📂 Upload Asset Data</h2>
            <p>Upload a CSV file or load sample data to see the dashboard in action.</p>
            
            <div class="upload-zone" onclick="document.getElementById('csvFile').click()">
                <span class="icon">📁</span>
                <div class="label">Click to select your CSV file</div>
                <div class="sub">or drag & drop</div>
                <input type="file" id="csvFile" accept=".csv" onchange="handleFileUpload(event)">
            </div>
            
            <button class="sample-btn" onclick="loadSampleData()">📊 Load Sample Data</button>
            <div class="download-link" onclick="downloadSampleCSV()">⬇️ Download sample CSV</div>
        </div>

        <!-- ===== DASHBOARD ===== -->
        <div class="dashboard" id="dashboard">
            <div class="timestamp" id="timestamp">📊 Data loaded: <span id="dataTime">—</span></div>
            
            <div class="kpi-grid" id="kpiGrid"></div>
            
            <div class="chart-container">
                <h3>📈 Daily Revenue Loss by Region</h3>
                <canvas id="lossChart"></canvas>
            </div>
            
            <div class="table-wrapper">
                <h3 style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">📋 Asset Table</h3>
                <div style="overflow-x: auto;">
                    <table id="dataTable">
                        <thead>
                            <tr>
                                <th>Site</th>
                                <th>City</th>
                                <th>Region</th>
                                <th>Status</th>
                                <th>Uptime</th>
                                <th>Daily Loss</th>
                            </tr>
                        </thead>
                        <tbody id="tableBody"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- ===== FOOTER ===== -->
        <div class="footer">
            <p>Free · No login · No data stored · Built with ❤️</p>
            <div class="badge-container">
                <span style="font-size: 12px; color: #4a5568;">📌 Listed on Turbo0</span>
                <a href="https://dang.ai/tool/cypher-ai-judge-chatbot" target="_blank" rel="dofollow noopener">
                    <img src="https://assets.dang.ai/badges/dang_verified-dark.png" alt="Verified on DANG!">
                </a>
                <a href="https://ko-fi.com/cypheryaps" target="_blank" style="display:inline-flex; align-items:center; gap:6px; text-decoration:none; background:#FFDD00; padding:4px 12px 4px 8px; border-radius:50px; font-weight:700; font-size:13px; color:#1a2b4c;">
                    <img src="https://storage.ko-fi.com/cdn/brandasset/kofi_brandtag.png" alt="Buy Me A Coffee" style="height:22px; width:auto;">
                    <span>Support</span>
                </a>
            </div>
        </div>
    </div>

    <div id="toast" class="toast">✅ File uploaded successfully!</div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script>
        var chartInstance = null;
        var currentData = [];

        // ============================================
        // SAMPLE DATA
        // ============================================
        function getSampleData() {
            return [
                { store: 'Site A', address: '123 Main St', city: 'Toronto', province: 'ON', zone: 'North', status: 'Online', volume: 245, volPriority: 'High', traffic: 1200, trend: '+5%', reject7d: '2.1%', impact: 'Medium', tem: '1.2%', paper: '78%', uptime: '99.8%', bin: '65%', serviceDays: 12, lastTx: '2026-09-02', version: 'v2.1', revenue: 45000, loss: 1200 },
                { store: 'Site B', address: '456 Queen St', city: 'Vancouver', province: 'BC', zone: 'West', status: 'Warning', volume: 89, volPriority: 'Medium', traffic: 450, trend: '-2%', reject7d: '8.7%', impact: 'High', tem: '5.4%', paper: '22%', uptime: '92.1%', bin: '89%', serviceDays: 45, lastTx: '2026-08-28', version: 'v1.9', revenue: 28000, loss: 3400 },
                { store: 'Site C', address: '789 King St', city: 'Montreal', province: 'QC', zone: 'East', status: 'Online', volume: 312, volPriority: 'High', traffic: 1800, trend: '+8%', reject7d: '1.8%', impact: 'Low', tem: '0.9%', paper: '95%', uptime: '100.0%', bin: '45%', serviceDays: 6, lastTx: '2026-09-02', version: 'v2.2', revenue: 62000, loss: 800 },
                { store: 'Site D', address: '321 Bay St', city: 'Calgary', province: 'AB', zone: 'West', status: 'Critical', volume: 45, volPriority: 'Low', traffic: 200, trend: '-12%', reject7d: '15.2%', impact: 'High', tem: '12.3%', paper: '8%', uptime: '85.5%', bin: '95%', serviceDays: 89, lastTx: '2026-07-15', version: 'v1.5', revenue: 15000, loss: 7800 },
                { store: 'Site E', address: '567 College St', city: 'Ottawa', province: 'ON', zone: 'East', status: 'Online', volume: 178, volPriority: 'Medium', traffic: 890, trend: '+3%', reject7d: '3.4%', impact: 'Medium', tem: '2.1%', paper: '67%', uptime: '98.9%', bin: '55%', serviceDays: 18, lastTx: '2026-09-01', version: 'v2.0', revenue: 35000, loss: 2100 },
                { store: 'Site F', address: '890 Granville St', city: 'Halifax', province: 'NS', zone: 'East', status: 'Offline', volume: 0, volPriority: 'Low', traffic: 0, trend: '-100%', reject7d: '0%', impact: 'Critical', tem: '0%', paper: '0%', uptime: '0.0%', bin: '100%', serviceDays: 120, lastTx: '2026-04-01', version: 'v1.2', revenue: 0, loss: 12000 }
            ];
        }

        function loadSampleData() {
            currentData = getSampleData();
            renderDashboard(currentData);
            showToast('✅ Sample data loaded! Explore the dashboard.');
            document.getElementById('uploadCard').style.display = 'none';
            document.getElementById('dashboard').classList.add('active');
        }

        function downloadSampleCSV() {
            const headers = ['store','address','city','province','zone','status','volume','volPriority','traffic','trend','reject7d','impact','tem','paper','uptime','bin','serviceDays','lastTx','version','revenue','loss'];
            const data = getSampleData();
            let csv = headers.join(',') + '\\n';
            data.forEach(row => {
                csv += headers.map(h => row[h] !== undefined ? row[h] : '').join(',') + '\\n';
            });
            const blob = new Blob([csv], { type: 'text/csv' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'sample-asset-data.csv';
            link.click();
        }

        // ============================================
        // FILE UPLOAD
        // ============================================
        function handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                const text = e.target.result;
                const lines = text.split('\\n').filter(line => line.trim());
                if (lines.length < 2) {
                    alert('The CSV file appears to be empty or invalid.');
                    return;
                }
                
                const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
                const data = [];
                for (let i = 1; i < lines.length; i++) {
                    const values = lines[i].split(',').map(v => v.trim());
                    const row = {};
                    headers.forEach((h, idx) => {
                        row[h] = values[idx] || '';
                    });
                    data.push(row);
                }
                
                currentData = data;
                renderDashboard(data);
                showToast('✅ ' + file.name + ' uploaded successfully!');
                document.getElementById('uploadCard').style.display = 'none';
                document.getElementById('dashboard').classList.add('active');
            };
            reader.readAsText(file);
        }

        // ============================================
        // RENDER DASHBOARD
        // ============================================
        function renderDashboard(data) {
            if (!data || data.length === 0) return;
            
            // Update timestamp
            document.getElementById('dataTime').textContent = new Date().toLocaleString();
            
            // KPI
            const totalRevenue = data.reduce((sum, r) => sum + (parseFloat(r.revenue) || 0), 0);
            const totalLoss = data.reduce((sum, r) => sum + (parseFloat(r.loss) || 0), 0);
            const avgUptime = data.reduce((sum, r) => sum + (parseFloat(r.uptime) || 0), 0) / data.length;
            const onlineCount = data.filter(r => r.status && r.status.toLowerCase() === 'online').length;
            
            document.getElementById('kpiGrid').innerHTML = `
                <div class="kpi-card"><div class="value">$${formatNumber(totalRevenue)}</div><div class="label">Total Revenue</div></div>
                <div class="kpi-card"><div class="value loss">$${formatNumber(totalLoss)}</div><div class="label">Total Loss</div></div>
                <div class="kpi-card"><div class="value">${avgUptime.toFixed(1)}%</div><div class="label">Avg Uptime</div></div>
                <div class="kpi-card"><div class="value">${onlineCount}/${data.length}</div><div class="label">Online</div></div>
            `;
            
            // Table
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = data.map(row => {
                const status = row.status || 'Unknown';
                const cls = status.toLowerCase() === 'critical' ? 'critical' : status.toLowerCase() === 'warning' ? 'warning' : '';
                return `<tr class="${cls}">
                    <td>${row.store || '-'}</td>
                    <td>${row.city || '-'}</td>
                    <td>${row.province || row.region || '-'}</td>
                    <td>${status}</td>
                    <td>${row.uptime || '-'}%</td>
                    <td>$${formatNumber(row.loss || 0)}</td>
                </tr>`;
            }).join('');
            
            // Chart
            const ctx = document.getElementById('lossChart').getContext('2d');
            if (chartInstance) chartInstance.destroy();
            
            const regionData = {};
            data.forEach(row => {
                const region = row.province || row.region || 'Unknown';
                regionData[region] = (regionData[region] || 0) + (parseFloat(row.loss) || 0);
            });
            
            chartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(regionData),
                    datasets: [{
                        label: 'Daily Loss ($)',
                        data: Object.values(regionData),
                        backgroundColor: 'rgba(220, 38, 38, 0.6)',
                        borderColor: 'rgba(220, 38, 38, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true } }
                }
            });
        }

        function formatNumber(num) {
            if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
            return num.toFixed(0);
        }

        // ============================================
        // RESET
        // ============================================
        function resetDashboard() {
            if (confirm('Reset the dashboard? You\'ll need to upload data again.')) {
                document.getElementById('dashboard').classList.remove('active');
                document.getElementById('uploadCard').style.display = 'block';
                document.getElementById('csvFile').value = '';
                currentData = [];
                if (chartInstance) { chartInstance.destroy(); chartInstance = null; }
                document.getElementById('kpiGrid').innerHTML = '';
                document.getElementById('tableBody').innerHTML = '';
            }
        }

        // ============================================
        // TOAST
        // ============================================
        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.style.display = 'block';
            setTimeout(() => { toast.style.display = 'none'; }, 3000);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    if 'session_id' not in session:
        session['session_id'] = f"user_{int(time.time())}_{os.urandom(4).hex()}"
    return render_template_string(
        HTML_TEMPLATE,
        bot_name=BOT_NAME,
        session_id=session['session_id']
    )

@app.route('/ping')
def ping():
    return jsonify({'status': 'ok', 'bot_name': BOT_NAME, 'fusion': 'Cypher Fusion (Non-US)'})

@app.route('/extract-image', methods=['POST'])
def extract_image():
    try:
        data = request.json
        file_content = data.get('file', '')
        file_name = data.get('name', 'image.jpg')
        result = extract_text_from_image(file_content, file_name)
        return jsonify({'text': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/extract-pdf', methods=['POST'])
def extract_pdf():
    try:
        data = request.json
        file_content = data.get('file', '')
        file_name = data.get('name', 'file.pdf')
        pdf_bytes = base64.b64decode(file_content)
        from io import BytesIO
        pdf_file = BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        if not text.strip():
            text = "No text could be extracted from this PDF."
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    global total_tokens_used, total_cost_usd
    data = request.json
    user_message = data.get('message', '').strip()
    session_id = data.get('session', session.get('session_id', 'default'))
    personality = data.get('personality', 'default')
    web_search = data.get('web_search', True)
    fusion_preset = data.get('fusion_preset', 'cypher_max')
    file_content = data.get('file_content', '')
    file_name = data.get('file_name', '')

    if not user_message:
        return jsonify({'error': 'No case presented.'}), 400

    if session_id not in chat_histories:
        chat_histories[session_id] = []

    history = chat_histories[session_id]
    personality_prompt = PERSONALITIES.get(personality, PERSONALITIES['default'])
    
    if file_content:
        personality_prompt += f"\n\nThe user submitted evidence named '{file_name}' with this content:\n\n{file_content[:6000]}\n\nUse this as evidence. If it's irrelevant, state that plainly."

    messages = [
        {"role": "system", "content": personality_prompt},
        {"role": "system", "content": "You are Cypher. Deliver one definitive ruling. No hedging. No check again. Just the verdict."},
        {"role": "system", "content": "If you're uncertain, state your confidence as a percentage. If you don't know, say I don't know."}
    ]
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": user_message})

    preset = CYPHER_PRESETS.get(fusion_preset, CYPHER_PRESETS["cypher_max"])
    
    try:
        payload = {
            "model": "openrouter/fusion",
            "plugins": [{
                "id": "fusion",
                "analysis_models": preset["panel"],
                "model": preset["judge"]
            }],
            "messages": messages,
            "temperature": 0.15,
            "max_tokens": 500,
            "top_p": 0.85,
        }
        if web_search:
            payload["tools"] = [{"type": "openrouter:web_search"}]

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {YOUR_API_KEY}",
                "Content-Type": "application/json",
                "X-OpenRouter-Cache": "true",
            },
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            error_msg = response.json().get('error', {}).get('message', 'API error')
            return jsonify({'error': f'Cypher Fusion Error: {error_msg}'})

        result = response.json()
        if not result or 'choices' not in result or not result['choices']:
            return jsonify({'error': 'Cypher gave no ruling.'})
        
        bot_reply = result['choices'][0]['message']['content']
        if not bot_reply:
            return jsonify({'error': 'No verdict generated.'})
        
        bot_reply = clean_claude_hedging(bot_reply)
        if not bot_reply.startswith(("Verdict:", "Ruling:", "Confidence:", "I don't know")):
            bot_reply = f"Ruling: {bot_reply}"
        
        html_reply = markdown.markdown(bot_reply, extensions=['tables', 'fenced_code'])
        html_reply = bleach.clean(html_reply, strip=True)
        
        usage = result.get('usage', {})
        total_tokens_used += usage.get('total_tokens', 0)
        total_cost_usd += 0.0001
        
        message_id = f"{session_id}_{int(time.time())}_{len(history)}"
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": bot_reply})
        if len(history) > 12:
            history = history[-12:]
            chat_histories[session_id] = history
        
        preset_name = preset["name"].split(" ")[0] + " " + preset["name"].split(" ")[1] if len(preset["name"].split(" ")) > 1 else preset["name"]
        return jsonify({
            'reply': bot_reply,
            'html_reply': html_reply,
            'message_id': message_id,
            'preset_used': preset_name,
            'score': preset["score"]
        })
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Cypher Fusion timed out.'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.json
        message_id = data.get('message_id')
        value = data.get('value')
        if not message_id or value not in [1, -1]:
            return jsonify({'error': 'Invalid feedback'}), 400
        if 'feedback_data' not in chat_histories:
            chat_histories['feedback_data'] = {}
        chat_histories['feedback_data'][message_id] = value
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear():
    session_id = request.json.get('session', session.get('session_id', 'default'))
    if session_id in chat_histories:
        chat_histories[session_id] = []
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False, threaded=True)