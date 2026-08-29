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

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-me')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# ========== READ FROM .env FILE ==========
YOUR_API_KEY = os.getenv('OPENROUTER_API_KEY')
BOT_NAME = os.getenv('BOT_NAME', 'Cypher')
# ===========================================

# ============================================
# PERSONALITY MODES
# ============================================

PERSONALITIES = {
    "default": f"""You are {BOT_NAME}, an advanced AI assistant with deep reasoning capabilities. 
You are warm, witty, and deeply helpful. You think step-by-step for complex problems and provide clear, 
well-structured answers. You're curious, ask clarifying questions when needed, and always aim to be 
accurate and insightful.""",

    "analyst": f"""You are {BOT_NAME} in ANALYST mode. You think in data, trends, and patterns.
You break down problems logically and present findings with clear structure.
You validate your conclusions and acknowledge uncertainty when present.
You're precise, evidence-based, and avoid speculation.
You use tables and bullet points to organize information when helpful.
You always ask clarifying questions before making assumptions.
You're helpful but direct — no fluff, just insights and actionable advice.""",

    "writer": f"""You are {BOT_NAME} in WRITER mode. You think in stories, metaphors, and vivid descriptions.
You craft responses that are engaging, creative, and easy to read.
You use descriptive language and avoid dry, technical explanations unless specifically asked.
You're warm, inviting, and make complex topics feel accessible.
You help users express ideas clearly and compellingly.
You're patient, encouraging, and offer constructive feedback on writing projects.
You're a creative partner — not just a fact-machine.""",

    "coder": f"""You are {BOT_NAME} in CODER mode. You think in logic, structure, and clean code.
You write Python, SQL, and other languages with best practices in mind.
You include error handling, type hints, and clear comments in your code.
You explain your approach before writing code.
You offer debugging help and suggest improvements.
You're precise, thorough, and avoid unnecessary explanations.
You assume the user has some technical background but explain complex parts clearly.""",

    "friend": f"""You are {BOT_NAME} in FRIEND mode. You're warm, casual, and conversational.
You respond like a supportive friend — empathetic, encouraging, and down-to-earth.
You use everyday language and avoid jargon unless asked.
You're great for general advice, brainstorming, or just chatting.
You're not judgmental and create a safe space for the user to express themselves.
You're helpful, but you also check in on how the user is feeling.
You keep things light and positive while still being genuinely useful."""
}

# Store chat history (per session)
chat_histories = {}
total_tokens_used = 0
total_cost_usd = 0.0

# ============================================
# HTML TEMPLATE - GENERIC FIELD ASSET DASHBOARD
# ============================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>Field Asset Intelligence | Real-Time Dashboard</title>
    <!-- External libraries -->
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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #f4f6fc;
            padding: 20px 16px;
            color: #1a2b4c;
            transition: background 0.3s, color 0.3s;
        }
        
        body.dark-mode {
            background: #0d1117;
            color: #c9d1d9;
        }
        
        .container { max-width: 1440px; margin: 0 auto; }
        
        .hero-header {
            background: linear-gradient(135deg, #0b1e3a 0%, #1f3a60 100%);
            border-radius: 36px;
            padding: 2rem 2.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 25px 45px -15px rgba(0,20,50,0.35);
            color: white;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
        }
        
        body.dark-mode .hero-header {
            background: linear-gradient(135deg, #0b1e3a 0%, #1f3a60 100%);
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
            background: rgba(220,38,38,0.25);
            backdrop-filter: blur(4px);
            padding: 5px 14px;
            border-radius: 40px;
            font-size: 0.75rem;
            font-weight: 600;
            color: #ffb3b3;
            border: 1px solid rgba(220,38,38,0.5);
        }
        
        .live-pulse::before {
            content: "";
            width: 8px;
            height: 8px;
            background: #ef4444;
            border-radius: 50%;
            display: inline-block;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            100% { opacity: 0.3; transform: scale(1.3); }
        }
        
        .hero-left .subtitle { color: #b9c8e0; margin-top: 8px; font-size: 0.95rem; }
        .hero-left .creator { color: #8899bb; font-size: 0.75rem; margin-top: 4px; }
        .hero-right { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
        
        .hero-btn {
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.25);
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
        
        .hero-btn:hover { background: rgba(255,255,255,0.25); transform: translateY(-2px); }
        .hero-btn.primary { background: #f0b90b; color: #0b1e3a; border: none; }
        
        .unified-card {
            max-width: 900px;
            margin: 0 auto 2.5rem auto;
            background: rgba(255,255,255,0.75);
            backdrop-filter: blur(12px);
            border-radius: 2rem;
            border: 1px solid rgba(255,255,255,0.9);
            box-shadow: 0 20px 35px -10px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        
        body.dark-mode .unified-card {
            background: rgba(22,27,34,0.75);
            border-color: rgba(48,54,61,0.5);
        }
        
        .card-section { padding: 2rem 2.5rem; text-align: center; }
        .card-section:first-child { border-bottom: 1px solid #edf1f9; }
        body.dark-mode .card-section:first-child { border-bottom: 1px solid #30363d; }
        
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
        
        body.dark-mode .section-title { color: #c9d1d9; }
        
        .upload-button {
            background: #eef2ff;
            border: 2px dashed #b9c8e0;
            border-radius: 20px;
            padding: 2rem;
            cursor: pointer;
            display: inline-block;
            transition: 0.2s;
        }
        
        body.dark-mode .upload-button {
            background: #161b22;
            border-color: #30363d;
        }
        
        .upload-button:hover { background: #e0e7ff; border-color: #4a5b6e; }
        body.dark-mode .upload-button:hover { background: #1a2332; border-color: #58a6ff; }
        
        .ops-links {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1rem;
            margin: 1.5rem 0;
        }
        
        .ops-links a {
            display: inline-flex;
            align-items: center;
            gap: 12px;
            color: #1e3a5f;
            text-decoration: none;
            font-weight: 500;
            transition: 0.2s;
        }
        
        body.dark-mode .ops-links a { color: #8b949e; }
        .ops-links a:hover { color: #0f2b44; transform: translateX(4px); }
        body.dark-mode .ops-links a:hover { color: #58a6ff; }
        
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
        
        body.dark-mode .mode-btn {
            background: #21262d;
            color: #8b949e;
        }
        
        .mode-btn.active { background: #1e3a5f; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        body.dark-mode .mode-btn.active { background: #1f3a60; }
        
        .mode-btn:hover:not(.active) { background: #cbd5e1; }
        body.dark-mode .mode-btn:hover:not(.active) { background: #30363d; }
        
        .dashboard.field-mode .office-only { display: none !important; }
        .dashboard.office-mode .field-only { display: none !important; }
        
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
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
        
        body.dark-mode .kpi-card {
            background: #161b22;
            border-color: #30363d;
        }
        
        .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 12px 24px rgba(0,0,0,0.06); }
        
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
        
        body.dark-mode .kpi-label { color: #8b949e; }
        .kpi-value { font-size: 28px; font-weight: 800; color: #1e293b; }
        body.dark-mode .kpi-value { color: #c9d1d9; }
        .kpi-loss { color: #dc2626; }
        
        .fleet-health-card {
            background: linear-gradient(135deg, #f0f4ff, #ffffff);
            border-radius: 24px;
            padding: 24px;
            margin-bottom: 28px;
            display: flex;
            align-items: center;
            gap: 24px;
            box-shadow: 0 8px 18px rgba(0,0,0,0.04);
            flex-wrap: wrap;
        }
        
        body.dark-mode .fleet-health-card {
            background: linear-gradient(135deg, #161b22, #21262d);
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
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        
        .chart-container, .map-container, .top-loss-container, .filters {
            background: white;
            border-radius: 24px;
            padding: 24px;
            margin-bottom: 28px;
            border: 1px solid #eef2f8;
            box-shadow: 0 6px 14px rgba(0,0,0,0.03);
        }
        
        body.dark-mode .chart-container, body.dark-mode .map-container, body.dark-mode .top-loss-container, body.dark-mode .filters {
            background: #161b22;
            border-color: #30363d;
        }
        
        .map-wrapper { display: flex; gap: 20px; flex-wrap: wrap; }
        .map-panel { flex: 2; min-width: 300px; }
        
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
        
        body.dark-mode .selection-panel {
            background: #0d1117;
            border-color: #30363d;
        }
        
        .selection-panel h4 { font-weight: 700; color: #0f2b44; margin-bottom: 12px; }
        body.dark-mode .selection-panel h4 { color: #c9d1d9; }
        
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
        
        body.dark-mode .selected-item {
            background: #161b22;
            border-color: #30363d;
        }
        
        .selected-item:hover { background: #eef2ff; }
        body.dark-mode .selected-item:hover { background: #1a2332; }
        .selected-item button { background: none; border: none; color: #dc2626; cursor: pointer; }
        
        .map-legend {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 12px;
            font-size: 11px;
            flex-wrap: wrap;
        }
        
        .map-legend-dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 4px; }
        
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
        
        body.dark-mode .top-loss-item { background: #0d1117; }
        .top-loss-item:hover { background: #eef2ff; }
        body.dark-mode .top-loss-item:hover { background: #1a2332; }
        
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
        
        .filter-group label { font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase; }
        body.dark-mode .filter-group label { color: #8b949e; }
        
        select, input, button {
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 0.85rem;
            border: 1px solid #e2e8f0;
            background: white;
        }
        
        body.dark-mode select, body.dark-mode input {
            background: #0d1117;
            border-color: #30363d;
            color: #c9d1d9;
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
        
        body.dark-mode button { background: #238636; }
        button:hover { background: #13273f; }
        body.dark-mode button:hover { background: #2ea043; }
        .reset-btn { background: #f1f5f9; color: #1e293b; border: 1px solid #e2e8f0; }
        body.dark-mode .reset-btn { background: #21262d; color: #8b949e; border-color: #30363d; }
        
        .table-wrapper {
            background: white;
            border-radius: 20px;
            overflow-x: auto;
            max-height: 480px;
            border: 1px solid #eef2f8;
            margin-bottom: 28px;
        }
        
        body.dark-mode .table-wrapper {
            background: #161b22;
            border-color: #30363d;
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
        
        body.dark-mode th {
            background: #0d1117;
            border-bottom-color: #30363d;
            color: #c9d1d9;
        }
        
        th:hover { background: #eef2ff; }
        body.dark-mode th:hover { background: #1a2332; }
        td { padding: 10px 8px; border-bottom: 1px solid #f1f5f9; white-space: nowrap; }
        body.dark-mode td { border-bottom-color: #30363d; }
        
        .critical-row { background-color: #fee2e2; }
        body.dark-mode .critical-row { background-color: #2d1a1a; }
        .warning-row { background-color: #fef3c7; }
        body.dark-mode .warning-row { background-color: #2d241a; }
        .selected-row { background-color: #dbeafe !important; }
        body.dark-mode .selected-row { background-color: #1a2332 !important; }
        
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 30px;
            font-size: 10px;
            font-weight: 600;
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
        
        body.dark-mode .priority-btn {
            background: #21262d;
            border-color: #30363d;
            color: #8b949e;
        }
        
        .priority-btn.active { background: #1e3a5f; color: white; border-color: #1e3a5f; }
        body.dark-mode .priority-btn.active { background: #238636; border-color: #238636; color: white; }
        .priority-btn:hover:not(.active) { background: #e2e8f0; }
        body.dark-mode .priority-btn:hover:not(.active) { background: #30363d; }
        
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
        
        body.dark-mode .alert-bar {
            background: #2d241a;
            border-left-color: #f59e0b;
            color: #c9d1d9;
        }
        
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
            width: 90%;
            text-align: center;
        }
        
        body.dark-mode .modal-content {
            background: #161b22;
            color: #c9d1d9;
        }
        
        .modal-content textarea {
            width: 100%;
            padding: 10px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            margin: 10px 0;
            resize: vertical;
        }
        
        body.dark-mode .modal-content textarea {
            background: #0d1117;
            border-color: #30363d;
            color: #c9d1d9;
        }
        
        .call-btn { background: #e2e8f0; border: none; padding: 6px 10px; border-radius: 20px; cursor: pointer; }
        body.dark-mode .call-btn { background: #30363d; color: #c9d1d9; }
        .notes-icon { cursor: pointer; margin-right: 6px; color: #3b82f6; }
        
        @media (max-width: 768px) {
            .hero-header { flex-direction: column; text-align: center; }
            .map-wrapper { flex-direction: column; }
            .kpi-grid { grid-template-columns: repeat(2, 1fr); }
        }
        
        @media (max-width: 480px) {
            .kpi-grid { grid-template-columns: 1fr; }
            .hero-header { padding: 1.5rem; }
            .card-section { padding: 1.5rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Hero header -->
        <div class="hero-header">
            <div class="hero-left">
                <h1><i class="fas fa-chart-line"></i> FIELD ASSET INTELLIGENCE <span class="live-pulse">LIVE</span></h1>
                <div class="subtitle">Real‑time fleet performance & predictive analytics</div>
                <div class="creator">Created by Your Company – Operations Expert</div>
            </div>
            <div class="hero-right" id="actionButtons" style="display:none;">
                <button class="hero-btn" id="showUploadBtn"><i class="fas fa-upload"></i> Upload CSV</button>
                <button class="hero-btn" id="qrBtn"><i class="fas fa-qrcode"></i> QR</button>
                <button class="hero-btn" id="snapshotBtn"><i class="fas fa-camera"></i> Screenshot</button>
                <button class="hero-btn primary" id="downloadPdfBtn"><i class="fas fa-file-pdf"></i> Executive PDF</button>
            </div>
        </div>

        <input type="file" id="csvFile" accept=".csv" style="display:none;" onchange="handleFileUpload(event)">

        <!-- Upload card -->
        <div id="uploadCard" class="unified-card">
            <div class="card-section">
                <div class="section-title"><i class="fas fa-cloud-upload-alt"></i> UPLOAD ASSET DATA</div>
                <div class="upload-instruction">Click to select your field asset CSV file</div>
                <div class="upload-button" id="uploadBtn" onclick="document.getElementById('csvFile').click()" style="cursor:pointer;">
                    <i class="fas fa-file-csv"></i><br>
                    <strong>Choose File</strong><br>
                    <small>or drag & drop</small>
                </div>
            </div>
            <div class="card-section">
                <div class="section-title"><i class="fas fa-toolbox"></i> FIELD OPERATIONS HUB</div>
                <div class="ops-links">
                    <a href="#"><i class="far fa-clock"></i> Timesheet</a>
                    <a href="#"><i class="fas fa-tools"></i> Knowledge Base</a>
                    <a href="#"><i class="fas fa-download"></i> Firmware & Software</a>
                    <a href="#"><i class="fas fa-shopping-cart"></i> Parts & Work Orders</a>
                </div>
                <div style="margin-top:1rem; font-size:0.8rem; color:#64748b;">
                    <i class="fas fa-envelope"></i> support@yourcompany.com
                </div>
            </div>
        </div>

        <!-- Dashboard -->
        <div id="dashboard" class="dashboard office-mode" style="display:none;">
            <div id="dataTimestamp" style="background:#eef2ff; padding:6px 16px; border-radius:20px; display:inline-block; margin-bottom:20px;"></div>

            <div class="mode-toggle-bar">
                <button id="fieldModeBtn" class="mode-btn" onclick="setMode('field')"><i class="fas fa-truck"></i> Field Mode</button>
                <button id="officeModeBtn" class="mode-btn active" onclick="setMode('office')"><i class="fas fa-chart-bar"></i> Office Mode</button>
                <span style="margin-left: auto; font-size:0.8rem; color:#64748b;" id="selectedSummary"></span>
            </div>

            <!-- Office-only sections -->
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

            <!-- Priority Buttons -->
            <div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:20px;" id="priorityButtons">
                <button class="priority-btn active" data-filter="all">📊 All</button>
                <button class="priority-btn" data-filter="urgent">🔥 High Impact</button>
                <button class="priority-btn" data-filter="high-reject">⚠️ High Failure</button>
                <button class="priority-btn" data-filter="full-bin">🗑️ Full Capacity</button>
                <button class="priority-btn" data-filter="paper-out">📄 Supply Low</button>
                <button class="priority-btn" data-filter="overdue">📅 Service Overdue</button>
                <button class="priority-btn" data-filter="high-tem">🔧 High Error</button>
                <button class="priority-btn" data-filter="high-volume">📊 High Activity</button>
                <button class="priority-btn" data-filter="call-first">📞 Offline</button>
            </div>

            <div class="alert-bar" id="alertBar"></div>

            <!-- Filters -->
            <div class="filters tech-detail">
                <div class="filter-group"><label>Region</label><select id="provinceFilter"><option value="all">All</option></select></div>
                <div class="filter-group"><label>Zone</label><select id="zoneFilter"><option value="all">All</option></select></div>
                <div class="filter-group"><label>Status</label><select id="riskFilter">
                    <option value="all">All</option>
                    <option value="critical">Critical</option>
                    <option value="warning">Warning</option>
                    <option value="good">Good</option>
                </select></div>
                <div class="filter-group"><label>Activity Priority</label><select id="volumePriorityFilter">
                    <option value="all">All</option>
                    <option value="High">High</option>
                    <option value="Mid">Mid</option>
                    <option value="Low">Low</option>
                </select></div>
                <div class="filter-group"><label>Search</label><input type="text" id="searchInput" placeholder="Site, city..."></div>
                <button id="resetBtn" class="reset-btn"><i class="fas fa-undo"></i> Reset</button>
            </div>

            <!-- Table -->
            <div class="table-wrapper tech-detail" id="tableWrapper" style="display:block;">
                <table id="dataTable">
                    <thead>
                        <tr>
                            <th><input type="checkbox" id="selectAllCheckbox"></th>
                            <th data-sort="store">Site</th>
                            <th data-sort="address">Address</th>
                            <th data-sort="city">City</th>
                            <th data-sort="province">Region</th>
                            <th data-sort="zone">Zone</th>
                            <th data-sort="status">Status</th>
                            <th data-sort="volume">Activity</th>
                            <th data-sort="volPriority">Activity Priority</th>
                            <th data-sort="traffic">Traffic</th>
                            <th data-sort="trend">Trend</th>
                            <th data-sort="reject7d">7D Failure%</th>
                            <th data-sort="impact">Impact</th>
                            <th data-sort="tem">Error Rate</th>
                            <th data-sort="paper">Supply</th>
                            <th data-sort="uptime">Uptime%</th>
                            <th data-sort="bin">Capacity%</th>
                            <th data-sort="serviceDays">Service Days</th>
                            <th data-sort="lastTx">Last Activity</th>
                            <th data-sort="version">Version</th>
                            <th data-sort="revenue">Est. Revenue</th>
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
                    <div class="map-panel"><div id="map" style="height:400px; border-radius
