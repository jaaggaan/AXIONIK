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

def get_dashboard_html() -> str:
    """Returns the full AXIONIK dashboard HTML string."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>AXIONIK — Retail Intelligence Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@400;600;700&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"/>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg-page:        #090a0f;
  --bg-card:        rgba(18, 19, 26, 0.85);
  --bg-card-solid:  #12131a;
  --bg-card-hover:  #191b26;
  --primary:        #6366f1;
  --success:        #10b981;
  --warning:        #f59e0b;
  --danger:         #ef4444;
  --text-main:      #f1f5f9;
  --text-muted:     #8892a4;
  --border:         #1d202d;
  --border-hover:   #2a2f42;
  --border-radius:  16px;
  --shadow:         0 8px 32px rgba(0, 0, 0, 0.5);
  --sidebar-width:  260px;
  --transition:     all 0.25s ease;
}
body {
  font-family: 'Inter', sans-serif;
  background-color: var(--bg-page);
  color: var(--text-main);
  min-height: 100vh;
  display: flex;
  overflow-x: hidden;
}
h1, h2, h3, h4, .logo-text { font-family: 'Sora', sans-serif; font-weight: 700; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
aside {
  width: var(--sidebar-width);
  height: 100vh;
  position: fixed;
  left: 0; top: 0;
  background: var(--bg-card-solid);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
  z-index: 100;
}
.logo-container { display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 0.75rem 2rem; }
.logo-icon { font-size: 1.4rem; color: var(--primary); }
.logo-text { font-size: 1.25rem; color: var(--text-main); }
.nav-item {
  display: flex; align-items: center; gap: 0.85rem; padding: 0.75rem 1rem;
  color: var(--text-muted); text-decoration: none; border-radius: 10px;
  font-weight: 500; cursor: pointer; transition: var(--transition);
}
.nav-item:hover, .nav-item.active { color: var(--text-main); background: var(--bg-card-hover); }
.nav-item.active { background: rgba(99, 102, 241, 0.15); color: var(--primary); box-shadow: inset 3px 0 0 0 var(--primary); }
.app-wrapper { margin-left: var(--sidebar-width); flex: 1; display: flex; flex-direction: column; min-height: 100vh; }
header {
  height: 68px; border-bottom: 1px solid var(--border);
  background: rgba(18, 19, 26, 0.5); backdrop-filter: blur(10px);
  display: flex; align-items: center; justify-content: space-between; padding: 0 2rem;
}
.search-wrapper { position: relative; width: 100%; max-width: 320px; }
.search-wrapper i { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: var(--text-muted); }
.search-input {
  width: 100%; background: var(--bg-card-solid); border: 1px solid var(--border);
  color: var(--text-main); padding: 0.55rem 1rem 0.55rem 2.5rem; border-radius: 10px;
  outline: none; font-size: 0.9rem; transition: var(--transition);
}
.search-input:focus { border-color: var(--primary); }
.header-right { display: flex; align-items: center; gap: 1rem; }
.live-pill {
  display: flex; align-items: center; gap: 0.45rem; padding: 0.35rem 0.8rem;
  border-radius: 999px; background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.25); font-size: 0.78rem; font-weight: 600; color: var(--success);
}
.live-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--success); }
main { flex: 1; padding: 2rem; display: flex; flex-direction: column; gap: 2rem; }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.25rem; }
.stat-card {
  background: var(--bg-card-solid); border: 1px solid var(--border);
  border-radius: var(--border-radius); padding: 1.5rem;
  display: flex; align-items: center; justify-content: space-between;
}
.stat-left { display: flex; flex-direction: column; gap: 0.35rem; }
.stat-label { font-size: 0.85rem; color: var(--text-muted); font-weight: 500; }
.stat-val { font-size: 1.75rem; font-weight: 700; }
.stat-icon-wrapper {
  width: 46px; height: 46px; border-radius: 12px;
  background: rgba(99, 102, 241, 0.15); color: var(--primary);
  display: grid; place-items: center; font-size: 1.25rem;
}
.bento-split { display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; }
.glass-card { background: var(--bg-card-solid); border: 1px solid var(--border); border-radius: var(--border-radius); padding: 1.5rem; }
.table-wrapper { border-radius: var(--border-radius); border: 1px solid var(--border); overflow: hidden; background: var(--bg-card-solid); }
table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem; }
th { color: var(--text-muted); font-weight: 600; padding: 1rem 1.25rem; font-size: 0.75rem; text-transform: uppercase; border-bottom: 1px solid var(--border); }
td { padding: 1rem 1.25rem; border-bottom: 1px solid var(--border); color: var(--text-main); }
tbody tr { cursor: pointer; transition: var(--transition); }
tbody tr:hover { background: var(--bg-card-hover); }
.badge { padding: 0.25rem 0.6rem; border-radius: 8px; font-size: 0.75rem; font-weight: 600; }
.vip-Platinum { background: rgba(168, 85, 247, 0.12); color: #c084fc; }
.vip-Gold { background: rgba(245, 158, 11, 0.12); color: #fbbf24; }
.vip-Silver { background: rgba(148, 163, 184, 0.12); color: #cbd5e1; }
.vip-Bronze { background: rgba(180, 83, 9, 0.12); color: #fb923c; }
.timeline { position: relative; padding-left: 20px; }
.timeline::before { content: ''; position: absolute; left: 4px; top: 4px; bottom: 4px; width: 2px; background: var(--border); }
.feed-item { position: relative; margin-bottom: 1.25rem; }
.feed-marker {
  position: absolute; left: -20px; width: 10px; height: 10px;
  border-radius: 50%; background: var(--primary); border: 2px solid var(--bg-page);
}
.feed-details { display: flex; flex-direction: column; gap: 2px; }
.feed-time { font-size: 0.68rem; color: var(--text-muted); }
.feed-desc { font-size: 0.8rem; line-height: 1.4; }
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0, 0, 0, 0.75); backdrop-filter: blur(8px);
  z-index: 1000; display: none; align-items: center; justify-content: center;
}
.modal-card {
  background: var(--bg-card-solid); border: 1px solid var(--border);
  border-radius: var(--border-radius); width: 100%; max-width: 480px;
  padding: 2rem; position: relative; display: flex; flex-direction: column; gap: 1.25rem;
}
.modal-close-btn { position: absolute; top: 1.25rem; right: 1.25rem; background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 1.1rem; }
.modal-close-btn:hover { color: var(--text-main); }
.modal-title { font-size: 1.25rem; margin-bottom: 0.5rem; }
.modal-info-row { display: flex; justify-content: space-between; border-bottom: 1px solid var(--border); padding: 0.5rem 0; font-size: 0.88rem; }
.modal-info-label { color: var(--text-muted); }
.modal-info-val { font-weight: 600; }
</style>
</head>
<body>
<aside>
  <div class="logo-container">
    <i class="fa-solid fa-cube logo-icon"></i>
    <span class="logo-text">AXIONIK</span>
  </div>
  <nav>
    <div class="nav-item active"><i class="fa-solid fa-chart-pie"></i><span>Dashboard</span></div>
  </nav>
</aside>
<div class="app-wrapper">
  <header>
    <div class="header-left">
      <div class="search-wrapper">
        <i class="fa-solid fa-magnifying-glass"></i>
        <input type="text" class="search-input" id="search-input" placeholder="Search customers..." oninput="handleSearch(this.value)">
      </div>
    </div>
    <div class="header-right">
      <div class="live-pill"><div class="live-dot"></div>Live</div>
    </div>
  </header>
  <main>
    <section class="stats-grid">
      <div class="stat-card">
        <div class="stat-left"><span class="stat-label">Total Customers</span><span class="stat-val" id="val-total">0</span></div>
        <div class="stat-icon-wrapper"><i class="fa-solid fa-users"></i></div>
      </div>
      <div class="stat-card">
        <div class="stat-left"><span class="stat-label">Active Now</span><span class="stat-val" id="val-active">0</span></div>
        <div class="stat-icon-wrapper"><i class="fa-solid fa-wifi"></i></div>
      </div>
      <div class="stat-card">
        <div class="stat-left"><span class="stat-label">Conversion Rate</span><span class="stat-val" id="val-conversion">0%</span></div>
        <div class="stat-icon-wrapper"><i class="fa-solid fa-chart-pie"></i></div>
      </div>
      <div class="stat-card">
        <div class="stat-left"><span class="stat-label">Revenue Today</span><span class="stat-val" id="val-revenue">$0.00</span></div>
        <div class="stat-icon-wrapper"><i class="fa-solid fa-sack-dollar"></i></div>
      </div>
    </section>
    <section class="bento-split">
      <div class="glass-card">
        <h3 style="margin-bottom: 1rem;">Recent Customers</h3>
        <div class="table-wrapper">
          <table>
            <thead>
              <tr><th>Customer</th><th>Phone</th><th>VIP Tier</th><th>Spend</th><th>Last Visit</th></tr>
            </thead>
            <tbody id="customers-table-body"></tbody>
          </table>
        </div>
      </div>
      <div class="glass-card">
        <h3 style="margin-bottom: 1rem;">Live Activity Feed</h3>
        <div class="timeline" id="activity-feed"></div>
      </div>
    </section>
  </main>
</div>
<div class="modal-overlay" id="customer-modal" onclick="closeCustomerModal(event)">
  <div class="modal-card" onclick="event.stopPropagation()">
    <button class="modal-close-btn" onclick="document.getElementById('customer-modal').style.display = 'none'">&times;</button>
    <h3 class="modal-title">Customer Dossier</h3>
    <div id="modal-content"></div>
  </div>
</div>
<script>
let customersData = [];
let activityData = [];
let filterQuery = '';

async function fetchTelemetry() {
  try {
    const custRes = await fetch('/api/customers');
    const actRes = await fetch('/api/activity');
    if (custRes.ok && actRes.ok) {
      customersData = await custRes.json();
      activityData = await actRes.json();
      updateDashboard();
    }
  } catch (err) { /* Ignore error */ }
}

function updateDashboard() {
  document.getElementById('val-total').innerText = customersData.length;
  const activeCount = activityData.filter(a => {
    const minDiff = (new Date() - new Date(a.timestamp)) / 60000;
    return minDiff <= 30;
  }).length;
  document.getElementById('val-active').innerText = activeCount;
  const connectedCount = activityData.filter(a => a.push_status === 'connected').length;
  const rate = activityData.length > 0 ? ((connectedCount / activityData.length) * 100).toFixed(1) + '%' : '0%';
  document.getElementById('val-conversion').innerText = rate;
  const totalSpend = customersData.reduce((acc, curr) => acc + (curr.total_spend || 0.0), 0.0);
  document.getElementById('val-revenue').innerText = '$' + totalSpend.toFixed(2);
  renderCustomersTable();
  renderActivityFeed();
}

function renderCustomersTable() {
  const tbody = document.getElementById('customers-table-body');
  tbody.innerHTML = '';
  const filtered = customersData.filter(c =>
    c.name.toLowerCase().includes(filterQuery.toLowerCase()) ||
    c.phone.includes(filterQuery)
  );
  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-muted)">No matching records</td></tr>';
    return;
  }
  filtered.forEach(c => {
    const tr = document.createElement('tr');
    tr.onclick = () => openCustomerModal(c);
    tr.innerHTML = `
      <td><strong>${c.name}</strong><br><span style="font-size:0.75rem;color:var(--text-muted)">${c.email || ''}</span></td>
      <td>${c.phone}</td>
      <td><span class="badge vip-${c.vip_tier}">${c.vip_tier}</span></td>
      <td>$${(c.total_spend || 0.0).toFixed(2)}</td>
      <td style="font-size:0.8rem;color:var(--text-muted)">${c.last_visit.replace('T',' ').slice(0,16)}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderActivityFeed() {
  const feed = document.getElementById('activity-feed');
  feed.innerHTML = '';
  if (activityData.length === 0) {
    feed.innerHTML = '<div style="color:var(--text-muted);font-size:0.8rem;">No activity log</div>';
    return;
  }
  activityData.slice(0, 10).forEach(a => {
    const div = document.createElement('div');
    div.className = 'feed-item';
    div.innerHTML = `
      <div class="feed-marker"></div>
      <div class="feed-details">
        <span class="feed-time">${a.timestamp.replace('T',' ').slice(11,16)}</span>
        <div class="feed-desc"><strong>${a.customer_name}</strong> connected at <strong>${a.store_name}</strong></div>
      </div>
    `;
    feed.appendChild(div);
  });
}

function handleSearch(val) { filterQuery = val; renderCustomersTable(); }

function openCustomerModal(c) {
  const modal = document.getElementById('customer-modal');
  const content = document.getElementById('modal-content');
  content.innerHTML = `
    <div class="modal-info-row"><span class="modal-info-label">Customer Name</span><span class="modal-info-val">${c.name}</span></div>
    <div class="modal-info-row"><span class="modal-info-label">Phone</span><span class="modal-info-val">${c.phone}</span></div>
    <div class="modal-info-row"><span class="modal-info-label">Email</span><span class="modal-info-val">${c.email || '—'}</span></div>
    <div class="modal-info-row"><span class="modal-info-label">VIP Category</span><span class="modal-info-val"><span class="badge vip-${c.vip_tier}">${c.vip_tier}</span></span></div>
    <div class="modal-info-row"><span class="modal-info-label">Lifetime Spend</span><span class="modal-info-val">$${(c.total_spend || 0.0).toFixed(2)}</span></div>
    <div class="modal-info-row"><span class="modal-info-label">Joined On</span><span class="modal-info-val">${c.created_at.replace('T',' ').slice(0,16)}</span></div>
    <div class="modal-info-row"><span class="modal-info-label">Last Visited</span><span class="modal-info-val">${c.last_visit.replace('T',' ').slice(0,16)}</span></div>
  `;
  modal.style.display = 'flex';
}

function closeCustomerModal(e) { document.getElementById('customer-modal').style.display = 'none'; }

window.addEventListener('load', () => { fetchTelemetry(); setInterval(fetchTelemetry, 5000); });
</script>
</body>
</html>"""
