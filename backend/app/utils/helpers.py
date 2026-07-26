# FILE: backend/app/utils/helpers.py
# DESCRIPTION: Shared utility functions and the dashboard HTML renderer

from __future__ import annotations

from fastapi import HTTPException
from typing import Any

# ---------------------------------------------------------------------------
# Store Registry
# ---------------------------------------------------------------------------

STORE_TECHHUB = "store_001"
STORE_URBAN = "store_002"
STORE_FRESHBITE = "store_003"

STORES: dict[str, dict[str, Any]] = {
    STORE_TECHHUB: {
        "store_id": STORE_TECHHUB,
        "name": "TechHub Electronics",
        "products": [
            "Wireless Earbuds Pro",
            "Smart Watch Series X",
            "USB-C Hub 7-in-1",
            "Portable Charger 20K",
            "Gaming Headset RGB",
        ],
        "offers": [
            "TODAY ONLY: 10% OFF Your Purchase!",
            "EXCLUSIVE: Free USB-C Cable with any order!"
        ],
    },
    STORE_URBAN: {
        "store_id": STORE_URBAN,
        "name": "Urban Style Fashion",
        "products": [
            "Summer Linen Dress",
            "Leather Crossbody Bag",
            "Running Sneakers",
            "Silk Scarf Collection",
            "Denim Jacket",
        ],
        "offers": [
            "TODAY ONLY: 20% OFF Summer Dresses!",
            "EXCLUSIVE: Free Leather Tote Bag on orders over $150!"
        ],
    },
    STORE_FRESHBITE: {
        "store_id": STORE_FRESHBITE,
        "name": "FreshBite Gourmet",
        "products": [
            "Artisan Sourdough Loaf",
            "Cold-Pressed Juice Flight",
            "Truffle Pasta Kit",
            "Organic Coffee Beans",
            "Seasonal Fruit Box",
        ],
        "offers": [
            "TODAY ONLY: Free Fresh Pastry with any Coffee!",
            "EXCLUSIVE: Buy One, Get One Free Artisan Sourdough!"
        ],
    },
}


def get_store(store_id: str) -> dict[str, Any]:
    """Retrieves store metadata by store ID."""
    store = STORES.get(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


def calculate_vip_tier(spend: float) -> str:
    """Calculates customer tier based on total spend value."""
    if spend >= 1000.0:
        return "Platinum"
    if spend >= 500.0:
        return "Gold"
    if spend >= 200.0:
        return "Silver"
    return "Bronze"


# ---------------------------------------------------------------------------
# Dashboard HTML Renderer
# ---------------------------------------------------------------------------

import os

DOCS_DASHBOARD_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "docs", "shopperstop_dashboard.html")
)

def get_dashboard_html() -> str:
    """Returns the full Shoppers Stop Admin Dashboard HTML string from docs/shopperstop_dashboard.html."""
    try:
        if os.path.isfile(DOCS_DASHBOARD_PATH):
            with open(DOCS_DASHBOARD_PATH, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        pass
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>SHOPPERS STOP — Retail Intelligence & Admin Reports</title>


  <!-- Google Fonts: Inter & JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@600;700&display=swap" rel="stylesheet">

  <!-- Font Awesome 6 -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

  <style>
    /* ==========================================================================
       DESIGN SYSTEM & CSS VARIABLES
       ========================================================================== */
    :root {
      --primary: #C41E3A;           /* Shoppers Stop Red */
      --primary-light: #FEF2F2;     /* Light Red Tint */
      --primary-hover: #A0182E;     /* Darker Red */
      --secondary: #C9A96E;         /* Muted Gold */
      --bg-main: #F8F9FA;           /* Light Gray Page Background */
      --bg-card: #FFFFFF;           /* Pure White */
      --text-main: #1A1A1A;         /* Near Black */
      --text-muted: #6B7280;        /* Gray Subtitles */
      --text-light: #9CA3AF;        /* Light Gray */
      --border-color: #E5E7EB;      /* Light Border */
      --border-hover: #D1D5DB;
      --success: #10B981;          /* Green */
      --warning: #F59E0B;          /* Amber */
      --danger: #EF4444;           /* Red */
      --info: #3B82F6;             /* Blue */
      
      --sidebar-width: 240px;
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.03);
      --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }

    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background-color: var(--bg-main);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      font-size: 14px;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }

    .font-mono {
      font-family: 'JetBrains Mono', monospace;
    }

    /* ==========================================================================
       SIDEBAR LAYOUT
       ========================================================================== */
    .sidebar {
      width: var(--sidebar-width);
      background-color: var(--bg-card);
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      height: 100vh;
      position: fixed;
      left: 0;
      top: 0;
      z-index: 100;
      padding: 24px 16px;
      transition: var(--transition);
    }

    .brand-header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 0 8px 24px 8px;
      border-bottom: 1px solid var(--border-color);
      margin-bottom: 24px;
    }

    .brand-logo-sq {
      width: 36px;
      height: 36px;
      background-color: var(--primary);
      color: #FFFFFF;
      font-family: 'Inter', sans-serif;
      font-weight: 800;
      font-size: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 8px;
      letter-spacing: -0.5px;
      box-shadow: 0 2px 4px rgba(196, 30, 58, 0.25);
      flex-shrink: 0;
    }

    .brand-title-wrap {
      display: flex;
      flex-direction: column;
    }

    .brand-name {
      font-weight: 800;
      font-size: 14px;
      letter-spacing: 0.5px;
      color: var(--text-main);
      line-height: 1.2;
    }

    .brand-tagline {
      font-size: 10px;
      color: var(--text-muted);
      font-weight: 500;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }

    .nav-section {
      display: flex;
      flex-direction: column;
      gap: 4px;
      flex: 1;
    }

    .nav-label {
      font-size: 11px;
      font-weight: 600;
      color: var(--text-light);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 8px 12px 4px 12px;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 14px;
      border-radius: var(--radius-md);
      color: var(--text-muted);
      text-decoration: none;
      font-weight: 500;
      font-size: 13.5px;
      transition: var(--transition);
      cursor: pointer;
      user-select: none;
    }

    .nav-item i {
      font-size: 16px;
      width: 20px;
      text-align: center;
      transition: var(--transition);
    }

    .nav-item:hover {
      background-color: var(--bg-main);
      color: var(--text-main);
    }

    .nav-item.active {
      background-color: var(--primary-light);
      color: var(--primary);
      font-weight: 600;
    }

    .nav-item.active i {
      color: var(--primary);
    }

    .sidebar-footer {
      border-top: 1px solid var(--border-color);
      padding-top: 16px;
      margin-top: auto;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    /* ==========================================================================
       MAIN CONTENT CONTAINER & TOP BAR
       ========================================================================== */
    .main-wrapper {
      margin-left: var(--sidebar-width);
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 100vh;
      width: calc(100% - var(--sidebar-width));
    }

    .top-bar {
      padding: 24px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
      background-color: var(--bg-main);
    }

    .page-header h1 {
      font-size: 24px;
      font-weight: 700;
      color: var(--text-main);
      letter-spacing: -0.02em;
    }

    .page-header p {
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    .filters-row {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .select-wrapper {
      position: relative;
    }

    .select-control {
      appearance: none;
      -webkit-appearance: none;
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 9px 36px 9px 14px;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-main);
      cursor: pointer;
      outline: none;
      transition: var(--transition);
      box-shadow: var(--shadow-sm);
    }

    .select-control:hover {
      border-color: var(--border-hover);
    }

    .select-control:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(196, 30, 58, 0.1);
    }

    .select-wrapper::after {
      content: "\\f078";
      font-family: "Font Awesome 6 Free";
      font-weight: 900;
      font-size: 10px;
      color: var(--text-muted);
      position: absolute;
      right: 14px;
      top: 50%;
      transform: translateY(-50%);
      pointer-events: none;
    }

    .btn-download {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 9px 16px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-main);
      cursor: pointer;
      transition: var(--transition);
      box-shadow: var(--shadow-sm);
    }

    .btn-download:hover {
      background-color: #F3F4F6;
      border-color: var(--border-hover);
    }

    .content-body {
      padding: 0 32px 32px 32px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    /* Tab Views */
    .tab-view {
      display: none;
      animation: fadeIn 0.25s ease-in-out forwards;
    }

    .tab-view.active {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* ==========================================================================
       CARDS, TABLES, & DASHBOARD COMPONENTS
       ========================================================================== */
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 16px;
    }

    .metric-card {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: var(--transition);
      box-shadow: var(--shadow-sm);
    }

    .metric-card:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
      border-color: var(--border-hover);
    }

    .metric-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 8px;
    }

    .metric-label {
      font-size: 11px;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .metric-icon-badge {
      width: 28px;
      height: 28px;
      border-radius: 6px;
      background-color: var(--bg-main);
      color: var(--text-muted);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
    }

    .metric-value {
      font-size: 26px;
      font-weight: 700;
      color: var(--text-main);
      line-height: 1.1;
      margin-bottom: 6px;
    }

    .metric-sub {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 11.5px;
      color: var(--text-muted);
    }

    .trend-pill {
      display: inline-flex;
      align-items: center;
      gap: 3px;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
    }

    .trend-up { background-color: #ECFDF5; color: var(--success); }
    .trend-down { background-color: #FEF2F2; color: var(--danger); }

    .sparkline-wrapper {
      margin-top: 10px;
      height: 28px;
      width: 100%;
    }

    .sparkline-svg {
      width: 100%;
      height: 100%;
      overflow: visible;
    }

    .sparkline-path {
      fill: none;
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
      stroke-dasharray: 200;
      stroke-dashoffset: 200;
      animation: drawSparkline 1.2s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }

    .sparkline-green { stroke: var(--success); }
    .sparkline-red { stroke: var(--danger); }
    .sparkline-gold { stroke: var(--secondary); }

    @keyframes drawSparkline {
      to { stroke-dashoffset: 0; }
    }

    .charts-grid {
      display: grid;
      grid-template-columns: 3fr 2fr;
      gap: 20px;
    }

    .card-panel {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 24px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
    }

    .panel-title {
      font-size: 16px;
      font-weight: 700;
      color: var(--text-main);
    }

    .barchart-container {
      position: relative;
      height: 260px;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding-top: 20px;
    }

    .chart-gridlines {
      position: absolute;
      top: 0;
      left: 36px;
      right: 0;
      bottom: 30px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      pointer-events: none;
    }

    .gridline {
      border-top: 1px dashed #F3F4F6;
      position: relative;
    }

    .gridline-label {
      position: absolute;
      left: -36px;
      top: -7px;
      font-size: 10px;
      color: var(--text-light);
      font-family: 'JetBrains Mono', monospace;
    }

    .bars-wrap {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      margin-left: 36px;
      height: 220px;
      position: relative;
      z-index: 2;
      padding-bottom: 4px;
    }

    .bar-col {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      height: 100%;
      justify-content: flex-end;
      position: relative;
      cursor: pointer;
    }

    .bar-pill {
      width: 60%;
      max-width: 24px;
      background-color: var(--primary);
      border-radius: 4px 4px 0 0;
      transition: height 0.6s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.2s ease;
    }

    .bar-col:hover .bar-pill {
      background-color: var(--primary-hover);
    }

    .bar-month {
      margin-top: 10px;
      font-size: 10px;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
    }

    .bar-tooltip {
      position: absolute;
      bottom: 100%;
      margin-bottom: 8px;
      background-color: var(--text-main);
      color: #FFFFFF;
      padding: 6px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      white-space: nowrap;
      pointer-events: none;
      opacity: 0;
      transform: translateY(4px);
      transition: var(--transition);
      box-shadow: var(--shadow-md);
      z-index: 10;
    }

    .bar-col:hover .bar-tooltip {
      opacity: 1;
      transform: translateY(0);
    }

    .category-list {
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    .cat-item {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .cat-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13px;
    }

    .cat-name { font-weight: 600; color: var(--text-main); }
    .cat-val { font-weight: 700; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }

    .progress-track {
      width: 100%;
      height: 8px;
      background-color: #F3F4F6;
      border-radius: 4px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      border-radius: 4px;
      transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .fill-ethnic { background: linear-gradient(90deg, #10B981, #34D399); }
    .fill-formal { background: linear-gradient(90deg, #3B82F6, #60A5FA); }
    .fill-beauty { background: linear-gradient(90deg, #C9A96E, #E5C384); }
    .fill-accessories { background: linear-gradient(90deg, #F59E0B, #FBBF24); }
    .fill-home { background: linear-gradient(90deg, #EF4444, #F87171); }

    .leaderboards-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }

    .leaderboard-list {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .leaderboard-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 14px;
      border-radius: var(--radius-md);
      transition: var(--transition);
      border-bottom: 1px solid #F3F4F6;
    }

    .leaderboard-row:hover { background-color: #F9FAFB; }

    .lb-left { display: flex; align-items: center; gap: 12px; }

    .lb-avatar {
      width: 38px; height: 38px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-weight: 700; font-size: 13px; color: #FFFFFF; flex-shrink: 0;
    }

    .lb-store-icon {
      width: 38px; height: 38px; border-radius: 10px;
      background-color: var(--primary-light); color: var(--primary);
      display: flex; align-items: center; justify-content: center;
      font-size: 16px; flex-shrink: 0;
    }

    .lb-info { display: flex; flex-direction: column; }
    .lb-name { font-weight: 600; color: var(--text-main); font-size: 13.5px; }
    .lb-sub { font-size: 11.5px; color: var(--text-muted); }
    .lb-right { display: flex; align-items: center; gap: 12px; }
    .lb-rank { font-size: 13px; font-weight: 700; color: var(--text-main); font-family: 'JetBrains Mono', monospace; }

    .vip-badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      margin-left: 6px;
    }
    .vip-Platinum { background-color: #F3E8FF; color: #7E22CE; }
    .vip-Gold { background-color: #FEF3C7; color: #B45309; }
    .vip-Silver { background-color: #F1F5F9; color: #475569; }
    .vip-Bronze { background-color: #FFEDD5; color: #C2410C; }

    /* Data Tables */
    .data-table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 13px;
    }

    .data-table th {
      padding: 12px 16px;
      font-weight: 600;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border-color);
      text-transform: uppercase;
      font-size: 11px;
      letter-spacing: 0.05em;
    }

    .data-table td {
      padding: 14px 16px;
      border-bottom: 1px solid var(--border-color);
      color: var(--text-main);
    }

    .data-table tbody tr:hover {
      background-color: #F9FAFB;
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 600;
    }
    .status-success { background-color: #ECFDF5; color: var(--success); }
    .status-warning { background-color: #FEF3C7; color: var(--warning); }
    .status-danger { background-color: #FEF2F2; color: var(--danger); }

    .btn-action {
      background: none;
      border: 1px solid var(--border-color);
      padding: 5px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-main);
      cursor: pointer;
      transition: var(--transition);
    }

    .btn-action:hover {
      background-color: var(--primary-light);
      color: var(--primary);
      border-color: var(--primary);
    }

    /* Search Bar Input */
    .search-input-wrap {
      position: relative;
      max-width: 320px;
      width: 100%;
    }

    .search-input-wrap i {
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: 13px;
    }

    .search-input-field {
      width: 100%;
      padding: 8px 14px 8px 36px;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      font-size: 13px;
      outline: none;
      transition: var(--transition);
    }

    .search-input-field:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(196, 30, 58, 0.1);
    }

    /* Modal Popup */
    .modal-backdrop {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background-color: rgba(0, 0, 0, 0.4);
      backdrop-filter: blur(4px);
      z-index: 200;
      display: none;
      align-items: center;
      justify-content: center;
    }

    .modal-backdrop.active {
      display: flex;
    }

    .modal-card {
      background-color: var(--bg-card);
      border-radius: var(--radius-lg);
      width: 100%;
      max-width: 480px;
      padding: 24px;
      box-shadow: var(--shadow-lg);
      position: relative;
      animation: modalSlide 0.25s ease-out forwards;
    }

    @keyframes modalSlide {
      from { opacity: 0; transform: translateY(16px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .modal-close {
      position: absolute;
      right: 16px;
      top: 16px;
      background: none;
      border: none;
      font-size: 18px;
      color: var(--text-muted);
      cursor: pointer;
    }

    /* Mobile Header */
    .mobile-header-bar {
      display: none;
      background-color: var(--bg-card);
      border-bottom: 1px solid var(--border-color);
      padding: 12px 20px;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 90;
    }

    .hamburger-btn {
      background: none;
      border: none;
      font-size: 20px;
      color: var(--text-main);
      cursor: pointer;
    }

    @media (max-width: 1200px) { .metrics-grid { grid-template-columns: repeat(3, 1fr); } }
    @media (max-width: 1024px) { .charts-grid, .leaderboards-grid { grid-template-columns: 1fr; } }
    @media (max-width: 768px) {
      .sidebar { transform: translateX(-100%); box-shadow: var(--shadow-lg); }
      .sidebar.open { transform: translateX(0); }
      .main-wrapper { margin-left: 0; width: 100%; }
      .mobile-header-bar { display: flex; }
      .top-bar { padding: 16px 20px; }
      .content-body { padding: 0 20px 20px 20px; }
      .metrics-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 480px) { .metrics-grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>

  <!-- MOBILE TOP BAR -->
  <div class="mobile-header-bar">
    <div style="display: flex; align-items: center; gap: 10px;">
      <div class="brand-logo-sq">SS</div>
      <span style="font-weight: 800; font-size: 15px;">SHOPPERS STOP</span>
    </div>
    <button class="hamburger-btn" id="sidebarToggleBtn" aria-label="Toggle Sidebar">
      <i class="fa-solid fa-bars"></i>
    </button>
  </div>

  <!-- SIDEBAR -->
  <aside class="sidebar" id="sidebar">
    <div class="brand-header">
      <div class="brand-logo-sq">SS</div>
      <div class="brand-title-wrap">
        <span class="brand-name">SHOPPERS STOP</span>
        <span class="brand-tagline">Stop. Style. Save.</span>
      </div>
    </div>

    <nav class="nav-section">
      <div class="nav-label">Main Menu</div>
      
      <a class="nav-item active" id="nav-dashboard" onclick="switchTab('view-dashboard', this, 'Reports', 'Retail Intelligence & Performance Analytics')">
        <i class="fa-solid fa-chart-pie"></i>
        <span>Dashboard</span>
      </a>

      <a class="nav-item" id="nav-orders" onclick="switchTab('view-orders', this, 'Orders Management', 'Track, search and inspect live customer orders')">
        <i class="fa-solid fa-bag-shopping"></i>
        <span>Orders</span>
      </a>

      <a class="nav-item" id="nav-customers" onclick="switchTab('view-customers', this, 'Customer Directory', 'Registered shoppers & VIP loyalty member list')">
        <i class="fa-solid fa-users"></i>
        <span>Customers</span>
      </a>

      <a class="nav-item" id="nav-inventory" onclick="switchTab('view-inventory', this, 'Inventory Control', 'Stock tracking & sell-through progress')">
        <i class="fa-solid fa-boxes-stacked"></i>
        <span>Inventory</span>
      </a>

      <a class="nav-item" id="nav-coupons" onclick="switchTab('view-coupons', this, 'Coupons & Promos', 'Active in-store discount campaigns')">
        <i class="fa-solid fa-ticket"></i>
        <span>Coupons</span>
      </a>

      <a class="nav-item" id="nav-analytics" onclick="switchTab('view-analytics', this, 'Analytics & Deep Insights', 'Comprehensive footfall & category intelligence')">
        <i class="fa-solid fa-chart-line"></i>
        <span>Analytics</span>
      </a>
    </nav>

    <div class="sidebar-footer">
      <div class="nav-label">Support</div>
      
      <a class="nav-item" onclick="openSupportModal('Help Center', 'Our 24/7 Retail Admin Helpdesk is ready to assist you. Call +1800-SHOPPERS or email support@shoppersstop.com')">
        <i class="fa-solid fa-circle-question"></i>
        <span>Help Center</span>
      </a>

      <a class="nav-item" onclick="openSupportModal('Admin Settings', 'System Configurations: Store Location: Phoenix Mall Bangalore | Currency: INR (₹) | API Sync: Active | Firebase Cloud: Connected')">
        <i class="fa-solid fa-gear"></i>
        <span>Settings</span>
      </a>
    </div>
  </aside>

  <!-- MAIN WRAPPER -->
  <div class="main-wrapper">
    
    <!-- TOP BAR -->
    <header class="top-bar">
      <div class="page-header">
        <h1 id="pageTitleText">Reports</h1>
        <p id="pageSubText">Retail Intelligence & Performance Analytics</p>
      </div>

      <div class="filters-row">
        <div class="select-wrapper">
          <select class="select-control" id="timeframeSelect" onchange="handleFilterChange()">
            <option value="all">All-time</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="year">This Year</option>
          </select>
        </div>

        <div class="select-wrapper">
          <select class="select-control" id="storeSelect" onchange="handleFilterChange()">
            <option value="all">All Stores</option>
            <option value="blr">Phoenix Mall, Bangalore</option>
            <option value="pune">Orion Mall, Pune</option>
            <option value="hyd">Inorbit, Hyderabad</option>
            <option value="chn">Forum, Chennai</option>
            <option value="koc">Lulu, Kochi</option>
          </select>
        </div>

        <div class="select-wrapper">
          <select class="select-control" id="categorySelect" onchange="handleFilterChange()">
            <option value="all">All Categories</option>
            <option value="ethnic">Women's Ethnic</option>
            <option value="formal">Men's Formal</option>
            <option value="beauty">Beauty & Fragrance</option>
            <option value="acc">Accessories</option>
            <option value="home">Home & Living</option>
          </select>
        </div>

        <button class="btn-download" onclick="triggerDownload()">
          <i class="fa-solid fa-download"></i>
          <span>Download</span>
        </button>
      </div>
    </header>

    <!-- CONTENT BODY CONTAINER FOR ALL TABS -->
    <main class="content-body">

      <!-- ===================================================================
           TAB 1: DASHBOARD VIEW (DEFAULT)
           =================================================================== -->
      <div id="view-dashboard" class="tab-view active">
        
        <!-- METRICS ROW (6 CARDS) -->
        <section class="metrics-grid">
          <div class="metric-card">
            <div class="metric-top">
              <span class="metric-label">Active Customers</span>
              <div class="metric-icon-badge"><i class="fa-solid fa-users"></i></div>
            </div>
            <div class="metric-value font-mono" id="m-active">27</div>
            <div class="metric-sub">
              <span class="trend-pill trend-up"><i class="fa-solid fa-arrow-up"></i> +5.2%</span>
              <span>in store now</span>
            </div>
            <div class="sparkline-wrapper">
              <svg class="sparkline-svg" viewBox="0 0 100 24">
                <path class="sparkline-path sparkline-green" d="M0 20 L25 15 L50 18 L75 8 L100 4" />
              </svg>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-top">
              <span class="metric-label">Orders Today</span>
              <div class="metric-icon-badge"><i class="fa-solid fa-bag-shopping"></i></div>
            </div>
            <div class="metric-value font-mono" id="m-orders">3,298</div>
            <div class="metric-sub">
              <span class="trend-pill trend-up"><i class="fa-solid fa-arrow-up"></i> +12.4%</span>
              <span>vs yesterday</span>
            </div>
            <div class="sparkline-wrapper">
              <svg class="sparkline-svg" viewBox="0 0 100 24">
                <path class="sparkline-path sparkline-green" d="M0 22 L25 19 L50 12 L75 8 L100 3" />
              </svg>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-top">
              <span class="metric-label">Avg. Cart Value</span>
              <div class="metric-icon-badge"><i class="fa-solid fa-receipt"></i></div>
            </div>
            <div class="metric-value font-mono" id="m-cart">₹2,847</div>
            <div class="metric-sub">
              <span class="trend-pill trend-up"><i class="fa-solid fa-arrow-up"></i> +3.1%</span>
              <span>per shopper</span>
            </div>
            <div class="sparkline-wrapper">
              <svg class="sparkline-svg" viewBox="0 0 100 24">
                <path class="sparkline-path sparkline-gold" d="M0 18 L25 14 L50 15 L75 10 L100 5" />
              </svg>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-top">
              <span class="metric-label">Conversion Rate</span>
              <div class="metric-icon-badge"><i class="fa-solid fa-percent"></i></div>
            </div>
            <div class="metric-value font-mono" id="m-conv">41.2%</div>
            <div class="metric-sub">
              <span class="trend-pill trend-up"><i class="fa-solid fa-arrow-up"></i> +2.3%</span>
              <span>walk-in ratio</span>
            </div>
            <div class="sparkline-wrapper">
              <svg class="sparkline-svg" viewBox="0 0 100 24">
                <path class="sparkline-path sparkline-green" d="M0 20 L25 16 L50 12 L75 11 L100 6" />
              </svg>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-top">
              <span class="metric-label">Inventory Turnover</span>
              <div class="metric-icon-badge"><i class="fa-solid fa-boxes-stacked"></i></div>
            </div>
            <div class="metric-value font-mono" id="m-inv">86%</div>
            <div class="metric-sub">
              <span class="trend-pill trend-up"><i class="fa-solid fa-arrow-up"></i> +5.0%</span>
              <span>sell-through rate</span>
            </div>
            <div class="sparkline-wrapper">
              <svg class="sparkline-svg" viewBox="0 0 100 24">
                <path class="sparkline-path sparkline-green" d="M0 21 L25 17 L50 13 L75 9 L100 4" />
              </svg>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-top">
              <span class="metric-label">Revenue Today</span>
              <div class="metric-icon-badge"><i class="fa-solid fa-indian-rupee-sign"></i></div>
            </div>
            <div class="metric-value font-mono" id="m-rev">₹1,14,999</div>
            <div class="metric-sub">
              <span class="trend-pill trend-up"><i class="fa-solid fa-arrow-up"></i> +8.7%</span>
              <span>gross sales</span>
            </div>
            <div class="sparkline-wrapper">
              <svg class="sparkline-svg" viewBox="0 0 100 24">
                <path class="sparkline-path sparkline-green" d="M0 24 L25 18 L50 14 L75 8 L100 2" />
              </svg>
            </div>
          </div>
        </section>

        <!-- CHARTS SECTION (2 COLUMNS) -->
        <section class="charts-grid">
          <div class="card-panel">
            <div class="panel-header">
              <h2 class="panel-title">Sales Activity</h2>
              <div class="select-wrapper">
                <select class="select-control" style="padding-top: 5px; padding-bottom: 5px; font-size: 12px;" onchange="updateBarChartData(this.value)">
                  <option value="year">Month (Jan-Dec)</option>
                  <option value="q1">Q1 Performance</option>
                  <option value="q2">Q2 Performance</option>
                </select>
              </div>
            </div>
            <div class="barchart-container">
              <div class="chart-gridlines">
                <div class="gridline"><span class="gridline-label">400k</span></div>
                <div class="gridline"><span class="gridline-label">300k</span></div>
                <div class="gridline"><span class="gridline-label">200k</span></div>
                <div class="gridline"><span class="gridline-label">100k</span></div>
                <div class="gridline"><span class="gridline-label">0</span></div>
              </div>
              <div class="bars-wrap" id="barsWrap"></div>
            </div>
          </div>

          <div class="card-panel">
            <div class="panel-header">
              <h2 class="panel-title">Top Performing Categories</h2>
              <span style="font-size: 12px; color: var(--text-muted); font-weight: 500;">Sales Contribution %</span>
            </div>
            <div class="category-list" id="categoryList"></div>
          </div>
        </section>

        <!-- LEADERBOARDS SECTION (2 COLUMNS) -->
        <section class="leaderboards-grid">
          <div class="card-panel">
            <div class="panel-header">
              <h2 class="panel-title">Top Customers</h2>
              <span style="font-size: 12px; color: var(--text-muted); font-weight: 500;">VIP Loyalty Tier</span>
            </div>
            <div class="leaderboard-list" id="customerLeaderboard"></div>
          </div>

          <div class="card-panel">
            <div class="panel-header">
              <h2 class="panel-title">Top Performing Stores</h2>
              <span style="font-size: 12px; color: var(--text-muted); font-weight: 500;">Target Achievement</span>
            </div>
            <div class="leaderboard-list" id="storeLeaderboard"></div>
          </div>
        </section>

      </div>

      <!-- ===================================================================
           TAB 2: ORDERS VIEW
           =================================================================== -->
      <div id="view-orders" class="tab-view">
        <div class="card-panel">
          <div class="panel-header">
            <h2 class="panel-title">Recent In-Store & Online Orders</h2>
            <div class="search-input-wrap">
              <i class="fa-solid fa-magnifying-glass"></i>
              <input type="text" class="search-input-field" placeholder="Search orders by ID or customer..." oninput="filterOrders(this.value)">
            </div>
          </div>

          <table class="data-table">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Category / Item</th>
                <th>Store</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody id="ordersTableBody">
              <tr>
                <td class="font-mono">#SS-9821</td>
                <td><strong>Priya Sharma</strong><br><span style="color:var(--text-muted);font-size:11px;">priya.s@email.com</span></td>
                <td>Silk Embroidered Saree</td>
                <td>Phoenix Mall, Bangalore</td>
                <td class="font-mono" style="font-weight:700;">₹12,499</td>
                <td><span class="status-badge status-success"><i class="fa-solid fa-circle-check"></i> Completed</span></td>
                <td><button class="btn-action" onclick="openSupportModal('Order #SS-9821 Details', 'Customer: Priya Sharma | Item: Silk Saree | Amount: ₹12,499 | Store: Bangalore Phoenix Mall | Payment: UPI Paid')">Receipt</button></td>
              </tr>
              <tr>
                <td class="font-mono">#SS-9820</td>
                <td><strong>Rahul Verma</strong><br><span style="color:var(--text-muted);font-size:11px;">rahul.v@email.com</span></td>
                <td>Men's Tailored Blazer</td>
                <td>Orion Mall, Pune</td>
                <td class="font-mono" style="font-weight:700;">₹8,990</td>
                <td><span class="status-badge status-success"><i class="fa-solid fa-circle-check"></i> Completed</span></td>
                <td><button class="btn-action" onclick="openSupportModal('Order #SS-9820 Details', 'Customer: Rahul Verma | Item: Men Blazer | Amount: ₹8,990 | Store: Pune Orion Mall | Payment: Card Paid')">Receipt</button></td>
              </tr>
              <tr>
                <td class="font-mono">#SS-9819</td>
                <td><strong>Ananya Gupta</strong><br><span style="color:var(--text-muted);font-size:11px;">ananya@email.com</span></td>
                <td>Channel Eau De Parfum</td>
                <td>Inorbit, Hyderabad</td>
                <td class="font-mono" style="font-weight:700;">₹14,500</td>
                <td><span class="status-badge status-warning"><i class="fa-solid fa-clock"></i> Processing</span></td>
                <td><button class="btn-action" onclick="openSupportModal('Order #SS-9819 Details', 'Customer: Ananya Gupta | Item: Perfume | Amount: ₹14,500 | Store: Hyderabad Inorbit | Payment: Pending at Counter')">Receipt</button></td>
              </tr>
              <tr>
                <td class="font-mono">#SS-9818</td>
                <td><strong>Marcus Johnson</strong><br><span style="color:var(--text-muted);font-size:11px;">marcus@email.com</span></td>
                <td>Leather Crossbody Bag</td>
                <td>Forum, Chennai</td>
                <td class="font-mono" style="font-weight:700;">₹6,250</td>
                <td><span class="status-badge status-success"><i class="fa-solid fa-circle-check"></i> Completed</span></td>
                <td><button class="btn-action" onclick="openSupportModal('Order #SS-9818 Details', 'Customer: Marcus Johnson | Item: Leather Bag | Amount: ₹6,250 | Store: Chennai Forum')">Receipt</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ===================================================================
           TAB 3: CUSTOMERS VIEW
           =================================================================== -->
      <div id="view-customers" class="tab-view">
        <div class="card-panel">
          <div class="panel-header">
            <h2 class="panel-title">Shoppers Stop VIP Members Directory</h2>
            <div class="search-input-wrap">
              <i class="fa-solid fa-magnifying-glass"></i>
              <input type="text" class="search-input-field" placeholder="Filter members by name or phone..." oninput="filterCustomerTable(this.value)">
            </div>
          </div>

          <table class="data-table">
            <thead>
              <tr>
                <th>Member Name</th>
                <th>Phone Number</th>
                <th>VIP Tier</th>
                <th>Total Spend</th>
                <th>Last In-Store Visit</th>
                <th>Profile Dossier</th>
              </tr>
            </thead>
            <tbody id="customersTableFullBody">
              <!-- Rendered via JavaScript -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- ===================================================================
           TAB 4: INVENTORY VIEW
           =================================================================== -->
      <div id="view-inventory" class="tab-view">
        <div class="card-panel">
          <div class="panel-header">
            <h2 class="panel-title">Store Stock & Category Sell-Through</h2>
            <button class="btn-download" onclick="alert('Exporting Inventory CSV...')"><i class="fa-solid fa-file-export"></i> Export Inventory</button>
          </div>

          <table class="data-table">
            <thead>
              <tr>
                <th>SKU Code</th>
                <th>Product Name</th>
                <th>Category</th>
                <th>Price</th>
                <th>Stock Level</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="font-mono">SKU-ETH-401</td>
                <td><strong>Designer Anarkali Suit</strong></td>
                <td>Women's Ethnic</td>
                <td class="font-mono">₹7,499</td>
                <td>
                  <div style="display:flex;align-items:center;gap:8px;">
                    <div class="progress-track" style="width:100px;"><div class="progress-fill fill-ethnic" style="width:85%;"></div></div>
                    <span class="font-mono" style="font-size:12px;font-weight:600;">85 pcs</span>
                  </div>
                </td>
                <td><span class="status-badge status-success">In Stock</span></td>
              </tr>
              <tr>
                <td class="font-mono">SKU-FOR-102</td>
                <td><strong>Italian Wool Tuxedo</strong></td>
                <td>Men's Formal</td>
                <td class="font-mono">₹18,990</td>
                <td>
                  <div style="display:flex;align-items:center;gap:8px;">
                    <div class="progress-track" style="width:100px;"><div class="progress-fill fill-formal" style="width:24%;"></div></div>
                    <span class="font-mono" style="font-size:12px;font-weight:600;">12 pcs</span>
                  </div>
                </td>
                <td><span class="status-badge status-warning">Low Stock</span></td>
              </tr>
              <tr>
                <td class="font-mono">SKU-BEA-882</td>
                <td><strong>MAC Matte Lipstick Velvet</strong></td>
                <td>Beauty & Fragrance</td>
                <td class="font-mono">₹2,150</td>
                <td>
                  <div style="display:flex;align-items:center;gap:8px;">
                    <div class="progress-track" style="width:100px;"><div class="progress-fill fill-beauty" style="width:92%;"></div></div>
                    <span class="font-mono" style="font-size:12px;font-weight:600;">140 pcs</span>
                  </div>
                </td>
                <td><span class="status-badge status-success">In Stock</span></td>
              </tr>
              <tr>
                <td class="font-mono">SKU-ACC-309</td>
                <td><strong>Fossil Gen 6 Smartwatch</strong></td>
                <td>Accessories</td>
                <td class="font-mono">₹14,995</td>
                <td>
                  <div style="display:flex;align-items:center;gap:8px;">
                    <div class="progress-track" style="width:100px;"><div class="progress-fill fill-home" style="width:5%;"></div></div>
                    <span class="font-mono" style="font-size:12px;font-weight:600;">2 pcs</span>
                  </div>
                </td>
                <td><span class="status-badge status-danger">Reorder Now</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ===================================================================
           TAB 5: COUPONS VIEW
           =================================================================== -->
      <div id="view-coupons" class="tab-view">
        <div class="card-panel">
          <div class="panel-header">
            <h2 class="panel-title">Active Campaign Promos & WiFi Coupons</h2>
            <button class="btn-download" style="background:var(--primary);color:#fff;border:none;" onclick="alert('Create New Promo Modal Opened!')"><i class="fa-solid fa-plus"></i> Create Coupon</button>
          </div>

          <table class="data-table">
            <thead>
              <tr>
                <th>Coupon Code</th>
                <th>Discount</th>
                <th>Target Category</th>
                <th>Total Uses</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong class="font-mono" style="color:var(--primary);font-size:14px;">STYLE10</strong></td>
                <td>10% OFF Entire Order</td>
                <td>All Categories</td>
                <td class="font-mono">1,420 redemptions</td>
                <td><span class="status-badge status-success">Active Live</span></td>
                <td><button class="btn-action" onclick="alert('Code STYLE10 copied to clipboard!')">Copy Code</button></td>
              </tr>
              <tr>
                <td><strong class="font-mono" style="color:var(--primary);font-size:14px;">FESTIVE20</strong></td>
                <td>20% OFF Ethnic Wear</td>
                <td>Women's Ethnic</td>
                <td class="font-mono">980 redemptions</td>
                <td><span class="status-badge status-success">Active Live</span></td>
                <td><button class="btn-action" onclick="alert('Code FESTIVE20 copied to clipboard!')">Copy Code</button></td>
              </tr>
              <tr>
                <td><strong class="font-mono" style="color:var(--primary);font-size:14px;">VIPGOLD500</strong></td>
                <td>Flat ₹500 Voucher</td>
                <td>Gold & Platinum VIPs</td>
                <td class="font-mono">312 redemptions</td>
                <td><span class="status-badge status-warning">Expiring Soon</span></td>
                <td><button class="btn-action" onclick="alert('Code VIPGOLD500 copied to clipboard!')">Copy Code</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ===================================================================
           TAB 6: ANALYTICS VIEW
           =================================================================== -->
      <div id="view-analytics" class="tab-view">
        <div class="card-panel">
          <div class="panel-header">
            <h2 class="panel-title">Footfall vs Conversion Analytics</h2>
          </div>
          <p style="color:var(--text-muted);margin-bottom:16px;">Detailed breakdown of in-store customer dwell time, conversion funnels, and repeat visitor retention across all regional flagship outlets.</p>
          <div class="metrics-grid">
            <div class="metric-card">
              <span class="metric-label">Avg. Dwell Time</span>
              <div class="metric-value font-mono">28.4 min</div>
              <span style="font-size:11px;color:var(--success);">+4.2 min vs avg</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Repeat Visitors</span>
              <div class="metric-value font-mono">64.8%</div>
              <span style="font-size:11px;color:var(--success);">High retention</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">WiFi Opt-in Rate</span>
              <div class="metric-value font-mono">82.1%</div>
              <span style="font-size:11px;color:var(--success);">+14% this month</span>
            </div>
          </div>
        </div>
      </div>

    </main>
  </div>

  <!-- SUPPORT / DOSSIER MODAL -->
  <div class="modal-backdrop" id="supportModal">
    <div class="modal-card">
      <button class="modal-close" onclick="closeModal()">&times;</button>
      <h3 id="modalTitle" style="font-size:18px;font-weight:700;margin-bottom:12px;color:var(--text-main);">Help Center</h3>
      <p id="modalBody" style="font-size:13px;color:var(--text-muted);line-height:1.6;"></p>
      <div style="margin-top:20px;text-align:right;">
        <button class="btn-download" style="background:var(--primary);color:#fff;border:none;" onclick="closeModal()">Close</button>
      </div>
    </div>
  </div>

  <!-- INTERACTIVE JAVASCRIPT LOGIC -->
  <script>
    /* ==========================================================================
       DATA SETS
       ========================================================================== */
    const barDataSets = {
      year: [
        { month: 'JAN', val: 120, label: '₹1,20,000' },
        { month: 'FEB', val: 150, label: '₹1,50,000' },
        { month: 'MAR', val: 180, label: '₹1,80,000' },
        { month: 'APR', val: 250, label: '₹2,50,000' },
        { month: 'MAY', val: 280, label: '₹2,80,000' },
        { month: 'JUN', val: 220, label: '₹2,20,000' },
        { month: 'JUL', val: 260, label: '₹2,60,000' },
        { month: 'AUG', val: 300, label: '₹3,00,000' },
        { month: 'SEP', val: 180, label: '₹1,80,000' },
        { month: 'OCT', val: 280, label: '₹2,80,000' },
        { month: 'NOV', val: 350, label: '₹3,50,000' },
        { month: 'DEC', val: 400, label: '₹4,00,000' }
      ],
      q1: [
        { month: 'JAN', val: 120, label: '₹1,20,000' },
        { month: 'FEB', val: 150, label: '₹1,50,000' },
        { month: 'MAR', val: 180, label: '₹1,80,000' }
      ],
      q2: [
        { month: 'APR', val: 250, label: '₹2,50,000' },
        { month: 'MAY', val: 280, label: '₹2,80,000' },
        { month: 'JUN', val: 220, label: '₹2,20,000' }
      ]
    };

    const categoriesData = [
      { name: "Women's Ethnic", pct: 95, class: "fill-ethnic" },
      { name: "Men's Formal", pct: 92, class: "fill-formal" },
      { name: "Beauty & Fragrance", pct: 89, class: "fill-beauty" },
      { name: "Accessories", pct: 74, class: "fill-accessories" },
      { name: "Home & Living", pct: 52, class: "fill-home" }
    ];

    let customersData = [];

    const storesData = [
      { name: 'Phoenix Mall, Bangalore', rev: '₹5.2L revenue', target: '97% target', rank: 'Rank 1', up: true },
      { name: 'Orion Mall, Pune', rev: '₹4.8L revenue', target: '94% target', rank: 'Rank 2', up: true },
      { name: 'Inorbit, Hyderabad', rev: '₹4.1L revenue', target: '89% target', rank: 'Rank 3', up: false },
      { name: 'Forum, Chennai', rev: '₹3.8L revenue', target: '85% target', rank: 'Rank 4', up: true },
      { name: 'Lulu, Kochi', rev: '₹3.2L revenue', target: '82% target', rank: 'Rank 5', up: false }
    ];

    /* ==========================================================================
       TAB VIEW SWITCHER (MAKES ALL BUTTONS RESPONSIVE & FUNCTIONAL)
       ========================================================================== */
    function switchTab(viewId, el, pageTitle, pageSub) {
      document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
      if (el) el.classList.add('active');

      document.querySelectorAll('.tab-view').forEach(v => v.classList.remove('active'));

      const target = document.getElementById(viewId);
      if (target) target.classList.add('active');

      document.getElementById('pageTitleText').innerText = pageTitle;
      document.getElementById('pageSubText').innerText = pageSub;

      // Close mobile drawer if open
      const sidebar = document.getElementById('sidebar');
      if (sidebar) sidebar.classList.remove('open');
    }

    /* ==========================================================================
       RENDER FUNCTIONS
       ========================================================================== */
    function renderBarChart(dataKey = 'year') {
      const wrap = document.getElementById('barsWrap');
      if (!wrap) return;
      wrap.innerHTML = '';
      const data = barDataSets[dataKey] || barDataSets.year;

      data.forEach(item => {
        const heightPct = (item.val / 400) * 100;
        const col = document.createElement('div');
        col.className = 'bar-col';
        col.innerHTML = `
          <div class="bar-tooltip">${item.label} — ${item.month}</div>
          <div class="bar-pill" style="height: 0%;" data-height="${heightPct}%"></div>
          <span class="bar-month">${item.month}</span>
        `;
        wrap.appendChild(col);
      });

      setTimeout(() => {
        const pills = wrap.querySelectorAll('.bar-pill');
        pills.forEach(pill => {
          pill.style.height = pill.getAttribute('data-height');
        });
      }, 50);
    }

    function updateBarChartData(key) {
      renderBarChart(key);
    }

    function renderCategories() {
      const list = document.getElementById('categoryList');
      if (!list) return;
      list.innerHTML = '';

      categoriesData.forEach(item => {
        const row = document.createElement('div');
        row.className = 'cat-item';
        row.innerHTML = `
          <div class="cat-header">
            <span class="cat-name">${item.name}</span>
            <span class="cat-val">${item.pct}%</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill ${item.class}" style="width: 0%" data-width="${item.pct}%"></div>
          </div>
        `;
        list.appendChild(row);
      });

      setTimeout(() => {
        const fills = list.querySelectorAll('.progress-fill');
        fills.forEach(fill => {
          fill.style.width = fill.getAttribute('data-width');
        });
      }, 50);
    }

    function loadLocalRegisteredCustomers() {
      try {
        const stored = localStorage.getItem('ss_registered_customers');
        if (stored) {
          const parsed = JSON.parse(stored);
          if (Array.isArray(parsed) && parsed.length > 0) {
            parsed.forEach(c => {
              if (c && c.name && !customersData.some(item => item.name === c.name || (c.phone && item.phone === c.phone))) {
                const nameParts = (c.name || 'User').split(' ');
                const inits = nameParts.length > 1 
                  ? (nameParts[0][0] + nameParts[1][0]).toUpperCase() 
                  : (c.name || 'U').slice(0, 2).toUpperCase();
                customersData.unshift({
                  name: c.name,
                  phone: c.phone || '+91 98765 43210',
                  spent: '₹' + (c.total_spend || 0).toLocaleString('en-IN'),
                  retention: '98%',
                  rank: 'Rank 1',
                  up: true,
                  bg: '#C41E3A',
                  initials: inits,
                  vip: c.vip_tier || 'Gold',
                  visit: c.last_visit || '2026-07-26 11:45'
                });
              }
            });
          }
        }
      } catch(e) {}
    }

    function renderCustomers() {
      loadLocalRegisteredCustomers();
      const list = document.getElementById('customerLeaderboard');
      if (!list) return;
      list.innerHTML = '';

      customersData.slice(0, 5).forEach((c, idx) => {
        const row = document.createElement('div');
        row.className = 'leaderboard-row';
        const trendIcon = c.up 
          ? '<span class="lb-trend up">▲</span>' 
          : '<span class="lb-trend down">▼</span>';

        const vipBadge = c.vip ? `<span class="vip-badge vip-${c.vip}">${c.vip}</span>` : '';

        row.innerHTML = `
          <div class="lb-left">
            <div class="lb-avatar" style="background-color: ${c.bg}">${c.initials}</div>
            <div class="lb-info">
              <span class="lb-name">${c.name} ${vipBadge}</span>
              <span class="lb-sub">${c.spent} spent • ${c.retention} retention</span>
            </div>
          </div>
          <div class="lb-right">
            <span class="lb-rank">${c.rank || ('Rank ' + (idx + 1))}</span>
            ${trendIcon}
          </div>
        `;
        list.appendChild(row);
      });

      renderFullCustomerTable();
    }

    function renderFullCustomerTable() {
      const tbody = document.getElementById('customersTableFullBody');
      if (!tbody) return;
      tbody.innerHTML = '';

      customersData.forEach(c => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>${c.name}</strong></td>
          <td class="font-mono">${c.phone || '+91 98000 11223'}</td>
          <td><span class="vip-badge vip-${c.vip || 'Bronze'}">${c.vip || 'Bronze'}</span></td>
          <td class="font-mono" style="font-weight:700;">${c.spent}</td>
          <td style="color:var(--text-muted);font-size:12px;">${c.visit || '2026-07-25 10:00'}</td>
          <td><button class="btn-action" onclick="openSupportModal('Customer Dossier: ${c.name}', 'Name: ${c.name} | Phone: ${c.phone} | VIP Tier: ${c.vip} | Total Lifetime Spend: ${c.spent} | Retention Score: ${c.retention}')">Inspect</button></td>
        `;
        tbody.appendChild(tr);
      });
    }

    function renderStores() {
      const list = document.getElementById('storeLeaderboard');
      if (!list) return;
      list.innerHTML = '';

      storesData.forEach(s => {
        const row = document.createElement('div');
        row.className = 'leaderboard-row';
        const trendIcon = s.up 
          ? '<span class="lb-trend up">▲</span>' 
          : '<span class="lb-trend down">▼</span>';

        row.innerHTML = `
          <div class="lb-left">
            <div class="lb-store-icon">
              <i class="fa-solid fa-store"></i>
            </div>
            <div class="lb-info">
              <span class="lb-name">${s.name}</span>
              <span class="lb-sub">${s.rev} • ${s.target}</span>
            </div>
          </div>
          <div class="lb-right">
            <span class="lb-rank">${s.rank}</span>
            ${trendIcon}
          </div>
        `;
        list.appendChild(row);
      });
    }

    /* ==========================================================================
       MODAL & FILTERS LOGIC
       ========================================================================== */
    function openSupportModal(title, body) {
      document.getElementById('modalTitle').innerText = title;
      document.getElementById('modalBody').innerText = body;
      document.getElementById('supportModal').classList.add('active');
    }

    function closeModal() {
      document.getElementById('supportModal').classList.remove('active');
    }

    function filterCustomerTable(query) {
      const rows = document.querySelectorAll('#customersTableFullBody tr');
      rows.forEach(r => {
        const text = r.innerText.toLowerCase();
        r.style.display = text.includes(query.toLowerCase()) ? '' : 'none';
      });
    }

    function filterOrders(query) {
      const rows = document.querySelectorAll('#ordersTableBody tr');
      rows.forEach(r => {
        const text = r.innerText.toLowerCase();
        r.style.display = text.includes(query.toLowerCase()) ? '' : 'none';
      });
    }

    function animateValue(id, start, end, duration, prefix = '', suffix = '') {
      const obj = document.getElementById(id);
      if (!obj) return;
      
      let startTimestamp = null;
      const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const currentVal = Math.floor(progress * (end - start) + start);
        let formatted = currentVal.toLocaleString('en-IN');
        obj.innerHTML = `${prefix}${formatted}${suffix}`;
        if (progress < 1) window.requestAnimationFrame(step);
      };
      window.requestAnimationFrame(step);
    }

    function runMetricsCountUp() {
      animateValue('m-active', 0, 27, 1200);
      animateValue('m-orders', 0, 3298, 1400);
      animateValue('m-cart', 0, 2847, 1300, '₹');
      animateValue('m-rev', 0, 114999, 1500, '₹');
    }

    /* API Telemetry Fetch — polls /api/customers and /api/activity every 5s */
    const colors = ['#C41E3A', '#C9A96E', '#3B82F6', '#10B981', '#8B5CF6', '#F59E0B'];

    function timeAgo(iso) {
      if (!iso) return 'Just now';
      const diff = Math.floor((Date.now() - new Date(iso)) / 1000);
      if (diff < 60) return diff + 's ago';
      if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
      if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
      return Math.floor(diff / 86400) + 'd ago';
    }

    function renderWifiActivityFeed(activities) {
      const container = document.getElementById('wifi-activity-feed');
      if (!container) return;
      if (!activities || activities.length === 0) {
        container.innerHTML = '<div style="padding:24px;text-align:center;color:var(--text-light);font-size:13px;">No WiFi check-ins yet. Waiting for customers…</div>';
        return;
      }
      const recent = activities.slice(0, 10);
      container.innerHTML = recent.map(a => {
        const nameParts = (a.name || 'Guest').split(' ');
        const inits = nameParts.length > 1
          ? (nameParts[0][0] + nameParts[1][0]).toUpperCase()
          : (a.name || 'G').slice(0, 2).toUpperCase();
        const isWifi = (a.source || '') === 'wifi_portal';
        return `<div class="leaderboard-row" style="border-left:3px solid ${isWifi ? 'var(--success)' : 'var(--primary)'};margin-bottom:4px;">
          <div class="lb-left">
            <div class="lb-avatar" style="background:${isWifi ? 'var(--success)' : 'var(--primary)'}">${inits}</div>
            <div class="lb-info">
              <div class="lb-name">${a.name || 'Guest'}
                <span style="font-size:10px;font-weight:600;padding:1px 7px;border-radius:4px;margin-left:6px;background:${isWifi ? '#ECFDF5' : 'var(--primary-light)'};color:${isWifi ? 'var(--success)' : 'var(--primary)'}">${isWifi ? 'WiFi' : 'Portal'}</span>
              </div>
              <div class="lb-sub">${a.phone || ''} · ${a.coupon || '—'} · ${timeAgo(a.timestamp)}</div>
            </div>
          </div>
          <div class="lb-right">
            <span class="status-badge status-success"><i class="fa-solid fa-wifi" style="font-size:9px"></i> Connected</span>
          </div>
        </div>`;
      }).join('');
    }

    async function fetchTelemetry() {
      try {
        const [custRes, actRes] = await Promise.all([
          fetch('/api/customers'),
          fetch('/api/activity')
        ]);
        if (!custRes.ok || !actRes.ok) return;

        const apiCust = await custRes.json();
        const apiAct  = await actRes.json();

        // ── Update WiFi activity feed (visible in Customers tab) ──
        renderWifiActivityFeed(apiAct);

        if (Array.isArray(apiCust) && apiCust.length > 0) {
          // Active in last 30 min
          const activeNow = Array.isArray(apiAct)
            ? apiAct.filter(a => (Date.now() - new Date(a.timestamp)) / 60000 <= 30).length
            : 0;

          const mActive = document.getElementById('m-active');
          if (mActive) mActive.innerText = activeNow || apiCust.length;

          // Total WiFi registrations metric
          const mWifi = document.getElementById('m-wifi-reg');
          if (mWifi) mWifi.innerText = apiCust.filter(c => c.source === 'wifi_portal').length;

          // Map customer data for the leaderboard
          customersData = apiCust.map((c, i) => {
            const nameParts = (c.name || 'User').split(' ');
            const inits = nameParts.length > 1
              ? (nameParts[0][0] + nameParts[1][0]).toUpperCase()
              : (c.name || 'U').slice(0, 2).toUpperCase();
            const lastSeen = c.last_seen || c.registered_at || '';
            return {
              name:      c.name || 'Customer',
              phone:     c.phone || '+91 98000 11223',
              spent:     '₹' + (c.total_spend || 0).toLocaleString('en-IN'),
              retention: (90 + (i % 8)) + '%',
              rank:      'Rank ' + (i + 1),
              up:        i % 2 === 0,
              bg:        colors[i % colors.length],
              initials:  inits,
              vip:       c.vip_tier || (c.source === 'wifi_portal' ? 'WiFi Guest' : 'Bronze'),
              visit:     lastSeen.replace('T', ' ').slice(0, 16),
              coupon:    c.coupon_used || '',
              discount:  c.discount_pct || 0,
              source:    c.source || '',
            };
          });

          renderCustomers();
        }
      } catch (err) { /* silently ignore network errors */ }
    }

    function handleFilterChange() {
      const timeframe = document.getElementById('timeframeSelect').value;
      const mult = timeframe === 'today' ? 0.3 : timeframe === 'week' ? 0.6 : 1.0;
      renderBarChart(timeframe === 'q1' ? 'q1' : timeframe === 'q2' ? 'q2' : 'year');
      animateValue('m-active', 0, Math.floor(27 * mult) + 5, 800);
      animateValue('m-orders', 0, Math.floor(3298 * mult) + 100, 800);
      animateValue('m-cart', 0, Math.floor(2847 * mult) + 50, 800, '₹');
      animateValue('m-rev', 0, Math.floor(114999 * mult) + 2000, 800, '₹');
    }

    function triggerDownload() {
      alert("Downloading SHOPPERS STOP Retail Performance Report (PDF)...");
    }

    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggleBtn');

    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
      });
    }

    // ── Init — runs immediately since <script> is at bottom of <body> ──────────
    (function initDashboard() {
      try {
        renderBarChart('year');
        renderCategories();
        renderCustomers();
        renderStores();
        runMetricsCountUp();
        renderWifiActivityFeed([]);
        fetchTelemetry();
        setInterval(fetchTelemetry, 5000);
      } catch(e) {
        console.error('Dashboard init error:', e);
      }
    })();
  </script>
</body>
</html>"""
