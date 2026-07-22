# FILE: main.py
# CLEANED: 2026-07-21
# DESCRIPTION: AXIONIK FastAPI backend — customer registration, orders, dashboard

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

import firebase_admin
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from firebase_admin import credentials, firestore
from pydantic import BaseModel, EmailStr, Field

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_PORT = 8000
FIREBASE_KEY_PATH = "firebase-key.json"
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

# ---------------------------------------------------------------------------
# Database Layer (Firestore with Local Memory Fallback)
# ---------------------------------------------------------------------------

db: firestore.firestore.Client | None = None
firebase_ready = False

# Local memory cache for database operations
_customers_cache: dict[str, dict[str, Any]] = {}
_visits_cache: list[dict[str, Any]] = []
_purchases_cache: dict[str, dict[str, Any]] = {}

# REMOVED: Unused Firestore collections and direct access logic

def init_firebase() -> None:
    """Initializes the Firebase Admin SDK client."""
    global db, firebase_ready
    try:
        if firebase_admin._apps:
            db = firestore.client()
            firebase_ready = True
            return
            
        cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", FIREBASE_KEY_PATH)
        if os.path.isfile(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            firebase_ready = True
            logger.info("Firebase Admin SDK & Firestore client initialized successfully")
        else:
            logger.warning("Firebase key file missing — running with local memory database fallback")
    except Exception as exc:
        logger.error("Firebase initialization failed: %s", exc)

init_firebase()

def seed_demo_data() -> None:
    """Seeds demo database records into local cache."""
    now_str = datetime.now(timezone.utc).isoformat()
    c1 = {
        "user_id": "cust_001",
        "name": "Sarah Chen",
        "phone": "+919876543210",
        "email": "sarah.chen@email.com",
        "vip_tier": "Platinum",
        "total_spend": 1250.0,
        "created_at": now_str,
        "last_visit": now_str
    }
    c2 = {
        "user_id": "cust_002",
        "name": "Marcus Johnson",
        "phone": "+919123456789",
        "email": "marcus.j@email.com",
        "vip_tier": "Gold",
        "total_spend": 520.0,
        "created_at": now_str,
        "last_visit": now_str
    }
    _customers_cache[c1["user_id"]] = c1
    _customers_cache[c2["user_id"]] = c2
    
    v1 = {
        "user_id": "cust_001",
        "customer_name": "Sarah Chen",
        "customer_phone": "+919876543210",
        "store_id": STORE_TECHHUB,
        "store_name": "TechHub Electronics",
        "platform": "ios",
        "timestamp": now_str,
        "push_status": "connected"
    }
    v2 = {
        "user_id": "cust_002",
        "customer_name": "Marcus Johnson",
        "customer_phone": "+919123456789",
        "store_id": STORE_URBAN,
        "store_name": "Urban Style Fashion",
        "platform": "android",
        "timestamp": now_str,
        "push_status": "connected"
    }
    _visits_cache.append(v1)
    _visits_cache.append(v2)

# Seed initial data
seed_demo_data()

def serialize_doc(data: dict[str, Any] | None) -> dict[str, Any] | None:
    """Serializes document datetimes to ISO string format."""
    if data is None:
        return None
    for key, value in list(data.items()):
        if isinstance(value, datetime):
            data[key] = value.isoformat().replace("+00:00", "Z")
    return data

def db_save_customer(customer_data: dict[str, Any]) -> dict[str, Any]:
    """Persists customer data to active store database."""
    user_id = customer_data["user_id"]
    if db is not None:
        db.collection("customers").document(user_id).set(customer_data)
    _customers_cache[user_id] = customer_data
    return customer_data

def db_get_customer(user_id: str) -> dict[str, Any] | None:
    """Retrieves customer profile by user ID."""
    if user_id in _customers_cache:
        return _customers_cache[user_id]
    if db is not None:
        doc = db.collection("customers").document(user_id).get()
        if doc.exists:
            data = doc.to_dict() or {}
            _customers_cache[user_id] = data
            return data
    return None

def db_list_customers() -> list[dict[str, Any]]:
    """Lists all customer profile directories."""
    if db is not None:
        docs = db.collection("customers").get()
        for doc in docs:
            _customers_cache[doc.id] = doc.to_dict() or {}
    return list(_customers_cache.values())

def db_save_visit(visit_data: dict[str, Any]) -> dict[str, Any]:
    """Saves a client check-in visit to database."""
    if db is not None:
        db.collection("visits").add(visit_data)
    _visits_cache.append(visit_data)
    return visit_data

def db_list_visits() -> list[dict[str, Any]]:
    """Lists recent check-in activities."""
    if db is not None:
        docs = db.collection("visits").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(100).get()
        visits_list = []
        for doc in docs:
            visits_list.append(serialize_doc(doc.to_dict() or {}))
        return visits_list
    return sorted(_visits_cache, key=lambda x: x.get("timestamp", ""), reverse=True)

def db_save_purchase(purchase_data: dict[str, Any]) -> dict[str, Any]:
    """Persists order purchase document."""
    purchase_id = purchase_data["id"]
    if db is not None:
        db.collection("purchases").document(purchase_id).set(purchase_data)
    _purchases_cache[purchase_id] = purchase_data
    return purchase_data

def db_get_purchase(purchase_id: str) -> dict[str, Any] | None:
    """Retrieves order details by purchase ID."""
    if purchase_id in _purchases_cache:
        return _purchases_cache[purchase_id]
    if db is not None:
        doc = db.collection("purchases").document(purchase_id).get()
        if doc.exists:
            data = doc.to_dict() or {}
            _purchases_cache[purchase_id] = data
            return data
    return None

# Helper functions
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
# FastAPI Initialization & Schema Models
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AXIONIK API",
    description="AXIONIK client node backend services",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class RegisterCustomerRequest(BaseModel):
    name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=5)
    email: EmailStr | None = None
    store_id: str = Field(..., min_length=1)
    consent: bool = True

class OrderRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    store_id: str = Field(..., min_length=1)
    product: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1)

# ---------------------------------------------------------------------------
# REST Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Returns backend service health status."""
    return {
        "status": "ok",
        "firebase_ready": firebase_ready,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/register-customer")
async def register_customer(body: RegisterCustomerRequest) -> dict[str, Any]:
    """Registers customer connection and stores visit logs."""
    try:
        now_str = datetime.now(timezone.utc).isoformat()
        user_id = f"user_{body.phone.replace('+', '')}"
        
        existing = db_get_customer(user_id)
        if existing:
            customer_data = {
                **existing,
                "name": body.name,
                "email": body.email or existing.get("email", ""),
                "last_visit": now_str,
                "consent": body.consent
            }
        else:
            customer_data = {
                "user_id": user_id,
                "name": body.name,
                "phone": body.phone,
                "email": body.email or "",
                "vip_tier": "Bronze",
                "total_spend": 0.0,
                "created_at": now_str,
                "last_visit": now_str,
                "consent": body.consent
            }
            
        db_save_customer(customer_data)
        
        store = get_store(body.store_id)
        visit_data = {
            "user_id": user_id,
            "customer_name": body.name,
            "customer_phone": body.phone,
            "store_id": body.store_id,
            "store_name": store["name"],
            "platform": "web",
            "timestamp": now_str,
            "push_status": "connected"
        }
        db_save_visit(visit_data)
        
        return {
            "status": "success",
            "user_id": user_id,
            "customer": customer_data
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("register_customer failed: %s", exc)
        raise HTTPException(status_code=500, detail="Registration failed") from exc

@app.get("/api/customers")
async def get_customers() -> list[dict[str, Any]]:
    """Returns registered client profiles list."""
    try:
        return db_list_customers()
    except Exception as exc:
        logger.error("get_customers failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve customers") from exc

@app.get("/api/activity")
async def get_activity() -> list[dict[str, Any]]:
    """Returns client check-in visits timeline list."""
    try:
        return db_list_visits()
    except Exception as exc:
        logger.error("get_activity failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve activities") from exc

@app.get("/api/menu/{store_id}")
async def get_menu(store_id: str) -> dict[str, Any]:
    """Returns store menus and promotion details."""
    store = get_store(store_id)
    return {
        "store_id": store_id,
        "name": store["name"],
        "products": store["products"],
        "offers": store["offers"]
    }

@app.post("/api/order")
async def place_order(body: OrderRequest) -> dict[str, Any]:
    """Processes visitor order transactions and updates VIP spend tags."""
    try:
        store = get_store(body.store_id)
        customer = db_get_customer(body.user_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer profile not found")
            
        now_str = datetime.now(timezone.utc).isoformat()
        order_id = f"ord_{int(datetime.now(timezone.utc).timestamp())}"
        
        purchase_data = {
            "id": order_id,
            "user_id": body.user_id,
            "store_id": body.store_id,
            "store_name": store["name"],
            "product": body.product,
            "amount": round(body.amount, 2),
            "category": body.category,
            "timestamp": now_str
        }
        db_save_purchase(purchase_data)
        
        new_spend = round(customer.get("total_spend", 0.0) + body.amount, 2)
        new_tier = calculate_vip_tier(new_spend)
        
        updated_customer = {
            **customer,
            "total_spend": new_spend,
            "vip_tier": new_tier,
            "last_visit": now_str
        }
        db_save_customer(updated_customer)
        
        return {
            "status": "success",
            "order_id": order_id,
            "purchase": purchase_data,
            "new_spend": new_spend,
            "vip_tier": new_tier
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("place_order failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to place order") from exc

@app.get("/api/order/{order_id}")
async def get_order(order_id: str) -> dict[str, Any]:
    """Retrieves specific order transaction details."""
    purchase = db_get_purchase(order_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Order record not found")
    return purchase

@app.get("/dashboard-ui")
async def dashboard_ui() -> HTMLResponse:
    """Renders the premium AXIONIK client management dashboard."""
    return HTMLResponse(_render_dashboard_ui())

# REMOVED: Unused settings, profile, export and push endpoints

# ---------------------------------------------------------------------------
# Dashboard UI Template Rendering
# ---------------------------------------------------------------------------

def _render_dashboard_ui() -> str:
    """Renders dashboard HTML template."""
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
  } catch (err) {
    // Ignore error
  }
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

function handleSearch(val) {
  filterQuery = val;
  renderCustomersTable();
}

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

function closeCustomerModal(e) {
  document.getElementById('customer-modal').style.display = 'none';
}

window.addEventListener('load', () => {
  fetchTelemetry();
  setInterval(fetchTelemetry, 5000);
});
</script>
</body>
</html>"""

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting AXIONIK FastAPI app on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
