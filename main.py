# FILE: main.py
# DESCRIPTION: AXIONIK FastAPI backend & Shoppers Stop Dashboard — Firebase Firestore Sync

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

import firebase_admin
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from firebase_admin import credentials, firestore
from pydantic import BaseModel, EmailStr, Field

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_PORT = 63265
FIREBASE_KEY_PATH = "firebase-key.json"
STORE_SHOPPERS_STOP = "store_shoppers_stop"

STORES: dict[str, dict[str, Any]] = {
    STORE_SHOPPERS_STOP: {
        "store_id": STORE_SHOPPERS_STOP,
        "name": "SHOPPERS STOP Flagship",
        "offers": [
            "TODAY ONLY: 20% OFF Welcome Voucher!",
            "EXCLUSIVE: Free Gift Voucher on purchases over ₹4,999!"
        ],
    }
}

# ---------------------------------------------------------------------------
# Database Layer (Firestore with Local Memory Fallback)
# ---------------------------------------------------------------------------

db: firestore.firestore.Client | None = None
firebase_ready = False

# ---------------------------------------------------------------------------
# Supabase PostgreSQL Integration (Unlimited Free Cloud Database)
# ---------------------------------------------------------------------------
supabase_client = None
supabase_ready = False

try:
    from supabase import create_client, Client
    supa_url = os.environ.get("SUPABASE_URL", "")
    supa_key = os.environ.get("SUPABASE_KEY", "")
    
    config_file = "supabase_config.json"
    if not supa_url and os.path.isfile(config_file):
        try:
            import json
            with open(config_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                supa_url = cfg.get("supabase_url", "")
                supa_key = cfg.get("supabase_key", "")
        except Exception as e:
            logger.warning("Could not parse supabase_config.json: %s", e)

    if supa_url and supa_key:
        supabase_client: Client = create_client(supa_url, supa_key)
        supabase_ready = True
        logger.info("✅ Supabase client connected successfully! URL: %s", supa_url)
    else:
        logger.info("ℹ️ Supabase credentials not set. Using local high-speed in-memory database fallback.")
except Exception as exc:
    logger.warning("Supabase initialization deferred: %s", exc)


# Local memory cache for database operations
_customers_cache: dict[str, dict[str, Any]] = {}
_visits_cache: list[dict[str, Any]] = []
_purchases_cache: dict[str, dict[str, Any]] = {}
_orders_cache: list[dict[str, Any]] = []
_redemptions_cache: list[dict[str, Any]] = []
_feedbacks_cache: list[dict[str, Any]] = [
    {
        "id": "REV-1001",
        "customerName": "Ananya Deshmukh",
        "customerEmail": "ananya.d@gmail.com",
        "customerPhone": "+91 98201 44321",
        "loyaltyTier": "Black",
        "storeLocation": "Mumbai - Malad West Flagship",
        "category": "Ethnic & Womenswear",
        "rating": 5,
        "title": "Exceptional Bridal Saree Consultation & Personal Styling",
        "comment": "The personal shopper service in the Ethnic Wear department was world-class. Staff gave expert fitting guidance and escorted us to the VIP Lounge. Seamless billing!",
        "date": "2026-08-02",
        "time": "16:45 PM",
        "sentiment": "Delighted",
        "verifiedPurchase": True,
        "helpfulCount": 24,
        "managerResponse": "Thank you Ananya! We are thrilled to hear about your bridal styling experience at Malad Flagship."
    }
]

_coupons_cache: list[dict[str, Any]] = [
    {
        "id": "CPN-101",
        "code": "FESTIVE20",
        "title": "Festive Discount",
        "description": "Flat 20% off on all Ethnic & Designer Collections for First Citizen Members",
        "discountType": "Percentage",
        "discountValue": 20,
        "minOrderValue": 4999,
        "usageCount": 1420,
        "maxUsage": 5000,
        "status": "Active",
        "startDate": "2026-07-01",
        "endDate": "2026-08-15",
        "applicableCategory": "Ethnic & Womenswear",
        "redemptions": [
            {
                "id": "RED-101",
                "couponId": "CPN-101",
                "couponCode": "FESTIVE20",
                "customerName": "Ananya Deshmukh",
                "customerEmail": "ananya.d@gmail.com",
                "customerPhone": "+91 98201 44512",
                "loyaltyTier": "Black",
                "orderId": "SS-ORD-98421",
                "orderTotal": 12999,
                "discountSaved": 2599,
                "redeemedAt": "2026-07-27 11:42 AM",
                "storeLocation": "Mumbai - Malad West Flagship"
            },
            {
                "id": "RED-102",
                "couponId": "CPN-101",
                "couponCode": "FESTIVE20",
                "customerName": "Priya Sundaram",
                "customerEmail": "priya.sundaram@tech.in",
                "customerPhone": "+91 99002 33110",
                "loyaltyTier": "Golden",
                "orderId": "SS-ORD-98419",
                "orderTotal": 7999,
                "discountSaved": 1600,
                "redeemedAt": "2026-07-27 10:50 AM",
                "storeLocation": "Bengaluru - MG Road Metro"
            },
            {
                "id": "RED-103",
                "couponId": "CPN-101",
                "couponCode": "FESTIVE20",
                "customerName": "Kavita Reddy",
                "customerEmail": "kavita.reddy@gmail.com",
                "customerPhone": "+91 97011 22900",
                "loyaltyTier": "Black",
                "orderId": "SS-ORD-98414",
                "orderTotal": 16000,
                "discountSaved": 3200,
                "redeemedAt": "2026-07-26 06:10 PM",
                "storeLocation": "Hyderabad - Inorbit Mall Hitec City"
            }
        ]
    },
    {
        "id": "CPN-102",
        "code": "FIRSTCITIZEN15",
        "title": "First Citizen Bonus",
        "description": "Exclusive 15% bonus discount for Black & Platinum tier members",
        "discountType": "Percentage",
        "discountValue": 15,
        "minOrderValue": 2999,
        "usageCount": 3840,
        "maxUsage": 10000,
        "status": "Active",
        "startDate": "2026-01-01",
        "endDate": "2026-12-31",
        "applicableCategory": "Site-wide",
        "redemptions": [
            {
                "id": "RED-201",
                "couponId": "CPN-102",
                "couponCode": "FIRSTCITIZEN15",
                "customerName": "Vikramaditya Roy",
                "customerEmail": "v.roy@consultant.com",
                "customerPhone": "+91 98112 09844",
                "loyaltyTier": "Platinum",
                "orderId": "SS-ORD-98420",
                "orderTotal": 8450,
                "discountSaved": 1267,
                "redeemedAt": "2026-07-27 11:15 AM",
                "storeLocation": "Delhi - Select CITYWALK Saket"
            }
        ]
    },
    {
        "id": "CPN-103",
        "code": "BEAUTYBUY2",
        "title": "Beauty Offer",
        "description": "Buy Beauty & Fragrance items above ₹5000 and get ₹1000 Instant Off",
        "discountType": "Flat Amount",
        "discountValue": 1000,
        "minOrderValue": 5000,
        "usageCount": 890,
        "maxUsage": 2500,
        "status": "Active",
        "startDate": "2026-07-10",
        "endDate": "2026-08-01",
        "applicableCategory": "Beauty & Perfumes",
        "redemptions": []
    },
    {
        "id": "CPN-104",
        "code": "ENDOFSEASON50",
        "title": "End of Season",
        "description": "End of Season Sale - Scheduled clearance for select Menswear lines",
        "discountType": "Percentage",
        "discountValue": 50,
        "minOrderValue": 9999,
        "usageCount": 0,
        "maxUsage": 1000,
        "status": "Scheduled",
        "startDate": "2026-08-05",
        "endDate": "2026-08-20",
        "applicableCategory": "Menswear",
        "redemptions": []
    }
]


def init_firebase(force_reload: bool = False) -> None:
    """Initializes the Firebase Admin SDK client with multi-path lookup."""
    global db, firebase_ready
    try:
        if firebase_admin._apps and not force_reload:
            db = firestore.client()
            firebase_ready = True
            return

        candidate_paths = [
            os.environ.get("FIREBASE_CREDENTIALS_PATH", ""),
            "firebase-key.json",
            "firebasekey.json",
            "firebase_key.json",
            "backend/firebase-key.json",
            "backend/firebasekey.json"
        ]
        # Also check any json file in directory containing 'firebase' or 'service_account'
        import glob
        for f in glob.glob("*.json") + glob.glob("backend/*.json"):
            if "firebase" in f.lower() or "adminsdk" in f.lower():
                candidate_paths.append(f)

        cred_path = None
        for p in candidate_paths:
            if p and os.path.isfile(p):
                cred_path = p
                break

        if cred_path:
            # Check if file contains template placeholders
            with open(cred_path, "r", encoding="utf-8") as f_cred:
                raw_cred = f_cred.read()
            if "YOUR_PRIVATE_KEY_HERE" in raw_cred or "YOUR_FIREBASE_PROJECT_ID" in raw_cred:
                logger.warning("Notice: %s contains template placeholders. Waiting for user to paste real key from Firebase Console.", cred_path)
                return
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            firebase_ready = True
            logger.info("Firebase Admin SDK & Firestore client initialized successfully from %s", cred_path)
        else:
            logger.warning("Firebase key file missing — running with local memory database fallback")
    except Exception as exc:
        logger.error("Firebase initialization failed: %s", exc)

init_firebase()

def ensure_firebase_ready():
    global firebase_ready
    if not firebase_ready:
        init_firebase(force_reload=True)
    return firebase_ready


def seed_demo_data() -> None:
    """Seeds demo database records into local cache and Firestore."""
    now_str = datetime.now(timezone.utc).isoformat()
    c1 = {
        "user_id": "cust_9876543210",
        "name": "Priya Sharma",
        "phone": "+919876543210",
        "email": "priya.sharma@email.com",
        "vip_tier": "Gold",
        "total_spend": 14999.0,
        "created_at": now_str,
        "last_visit": now_str
    }
    c2 = {
        "user_id": "cust_9123456789",
        "name": "Rahul Verma",
        "phone": "+919123456789",
        "email": "rahul.v@email.com",
        "vip_tier": "Platinum",
        "total_spend": 28400.0,
        "created_at": now_str,
        "last_visit": now_str
    }
    _customers_cache[c1["user_id"]] = c1
    _customers_cache[c2["user_id"]] = c2

    v1 = {
        "user_id": "cust_9876543210",
        "customer_name": "Priya Sharma",
        "customer_phone": "+919876543210",
        "store_id": STORE_SHOPPERS_STOP,
        "store_name": "SHOPPERS STOP Flagship",
        "platform": "ESP32_WiFi",
        "timestamp": now_str,
        "push_status": "connected"
    }
    _visits_cache.append(v1)

seed_demo_data()

def db_save_customer(customer_data: dict[str, Any]) -> dict[str, Any]:
    supabase_save_customer(customer_data)
    """Persists customer profile to Firestore and memory cache."""
    user_id = customer_data["user_id"]
    if db is not None:
        try:
            db.collection("customers").document(user_id).set(customer_data)
        except Exception as e:
            logger.error("Firestore customer save error: %s", e)
    _customers_cache[user_id] = customer_data
    return customer_data

def db_get_customer(user_id: str) -> dict[str, Any] | None:
    """Retrieves customer profile by ID."""
    if user_id in _customers_cache:
        return _customers_cache[user_id]
    if db is not None:
        try:
            doc = db.collection("customers").document(user_id).get()
            if doc.exists:
                data = doc.to_dict() or {}
                _customers_cache[user_id] = data
                return data
        except Exception as e:
            logger.error("Firestore customer fetch error: %s", e)
    return None

def db_list_customers() -> list[dict[str, Any]]:
    """Returns list of registered customer profiles."""
    if db is not None:
        try:
            docs = db.collection("customers").get()
            res = []
            for doc in docs:
                data = doc.to_dict() or {}
                res.append(data)
            if res:
                return res
        except Exception as e:
            logger.error("Firestore customer list error: %s", e)
    return list(_customers_cache.values())

def db_save_visit(visit_data: dict[str, Any]) -> None:
    """Persists visit check-in record."""
    if db is not None:
        try:
            db.collection("visits").add(visit_data)
        except Exception as e:
            logger.error("Firestore visit save error: %s", e)
    _visits_cache.insert(0, visit_data)

def db_list_visits() -> list[dict[str, Any]]:
    """Returns visit check-in feed."""
    if db is not None:
        try:
            docs = db.collection("visits").limit(20).get()
            res = [d.to_dict() for d in docs if d.exists]
            if res:
                return res
        except Exception as e:
            logger.error("Firestore visits list error: %s", e)
    return _visits_cache

def calculate_vip_tier(spend: float) -> str:
    """Calculates customer VIP status based on spend."""
    if spend >= 20000.0:
        return "Platinum"
    if spend >= 10000.0:
        return "Gold"
    if spend >= 3000.0:
        return "Silver"
    return "Bronze"

# ---------------------------------------------------------------------------
# FastAPI Initialization & Endpoints
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AXIONIK — SHOPPERS STOP Portal Backend",
    description="Captive Portal, Real-Time Dashboard & Firebase Firestore Engine",
    version="3.5.0"
)

# Serve dashboard React assets
try:
    app.mount("/assets", StaticFiles(directory=r"c:\Users\rentk\Projects\freesalewifi\frontend\shopperstop-dashboard-app\dist\assets"), name="dash_assets")
except Exception as _e:
    print(f"Warning: Could not mount dashboard assets: {_e}")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class SigninPayload(BaseModel):
    name: str
    phone: str
    email: str | None = ""

class CouponPayload(BaseModel):
    code: str
    title: str | None = "Special Offer"
    discountType: str | None = "percentage"
    discountValue: float = 10.0
    minOrderValue: float = 1000.0
    description: str | None = ""
    endDate: str | None = "31 Dec 2026"

@app.get("/health")
async def health_check() -> dict[str, Any]:
    return {
        "status": "online",
        "firebase_ready": firebase_ready,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/api/customers")
async def create_customer(body: dict[str, Any]) -> dict[str, Any]:
    name = body.get("name", "Wi-Fi Guest")
    phone = body.get("phone", "+91 98201 00000")
    email = body.get("email", f"{phone}@ss-wifi.in")
    user_id = f"cust_{str(phone).replace('+', '').replace(' ', '')}"

    cust = db_get_customer(user_id)
    if not cust:
        cust = {
            "user_id": user_id,
            "customer_id": user_id,
            "name": name,
            "email": email,
            "phone": phone,
            "vip_tier": "Silver",
            "total_spend": 0.0,
            "points": 500,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    else:
        cust["name"] = name
        cust["email"] = email or cust.get("email", "")
    
    db_save_customer(cust)
    return {"success": True, "status": "ok", "customer": cust}

@app.get("/api/customers")
async def get_customers() -> dict[str, Any]:
    return {"success": True, "customers": db_list_customers()}

@app.get("/api/activity")
async def get_activity() -> list[dict[str, Any]]:
    return db_list_visits()

@app.post("/api/signin")
async def api_signin(body: SigninPayload) -> dict[str, Any]:
    now_str = datetime.now(timezone.utc).isoformat()
    user_id = f"cust_{body.phone.replace('+', '')}"

    existing = db_get_customer(user_id)
    if existing:
        cust = {
            **existing,
            "name": body.name,
            "email": body.email or existing.get("email", ""),
            "last_visit": now_str
        }
    else:
        cust = {
            "user_id": user_id,
            "name": body.name,
            "phone": body.phone,
            "email": body.email or "",
            "vip_tier": "Gold",
            "total_spend": 0.0,
            "created_at": now_str,
            "last_visit": now_str
        }

    db_save_customer(cust)

    print("\n==================================================================", flush=True)
    print(f"★ REAL-TIME ESP32 WI-FI SIGN-IN RECEIVED VIA PORTAL ★", flush=True)
    print(f"Customer: {body.name} | Phone: {body.phone} | Email: {body.email}", flush=True)
    print("==================================================================\n", flush=True)

    if firebase_ready and db:
        try:
            db.collection("customers").document(body.email or user_id).set({
                "id": f"FC-{int(datetime.now().timestamp())%100000}",
                "username": body.name,
                "email": body.email or "",
                "phone": body.phone,
                "loyaltyTier": "Black",
                "lastVisitAt": now_str
            }, merge=True)
            logger.info("Synced Wi-Fi signin for %s to Firestore!", body.name)
        except Exception as e:
            logger.error("Firestore Wi-Fi signin sync error: %s", e)

    visit = {
        "user_id": user_id,
        "customer_name": body.name,
        "customer_phone": body.phone,
        "store_id": STORE_SHOPPERS_STOP,
        "store_name": "SHOPPERS STOP Flagship",
        "platform": "ESP32_WiFi",
        "timestamp": now_str,
        "push_status": "connected"
    }
    db_save_visit(visit)

    return {"status": "success", "customer": cust}

@app.get("/api/coupons")
async def get_coupons() -> dict[str, Any]:
    return {"success": True, "coupons": _coupons_cache}

@app.post("/api/coupons")
async def create_coupon(body: CouponPayload) -> dict[str, Any]:
    c = body.dict()
    c["code"] = c["code"].upper()
    _coupons_cache.insert(0, c)
    if db is not None:
        try:
            db.collection("coupons").document(c["code"]).set(c)
        except Exception as e:
            logger.error("Firestore coupon save error: %s", e)
    return {"success": True, "coupon": c}


# ---------------------------------------------------------------------------
# Order Processing & MCP Integration Engine (Claude / Axionik Marketplace)
# ---------------------------------------------------------------------------

def process_live_order(body: dict[str, Any]) -> dict[str, Any]:
    """Process an order from Captive Portal, Dashboard, or Claude MCP Connector."""
    import uuid
    order_id = body.get("orderId") or body.get("order_id") or f"SS-ORD-{uuid.uuid4().hex[:6].upper()}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    user_info = body.get("user") or {}
    cust_name = user_info.get("name") or body.get("customerName") or "Shoppers Stop Guest"
    cust_phone = user_info.get("phone") or body.get("customerPhone") or "+91 98201 00000"
    cust_email = user_info.get("email") or body.get("customerEmail") or "guest@shoppersstop.com"
    
    items = body.get("items", [])
    order_total = body.get("finalTotal") or body.get("totalAmount") or sum(i.get("price", 0) * i.get("qty", 1) for i in items) or 2499.0
    coupon_code = (body.get("couponCode") or body.get("coupon") or "").strip().upper()
    discount_saved = body.get("discountSaved") or (order_total * 0.15 if coupon_code else 0.0)
    store_loc = body.get("storeLocation") or "Mumbai - Malad West Flagship"

    # 1. Update or create Customer profile
    user_id = f"cust_{str(cust_phone).replace('+', '').replace(' ', '')}"
    cust = db_get_customer(user_id)
    if not cust:
        cust = {
            "user_id": user_id,
            "customer_id": user_id,
            "name": cust_name,
            "email": cust_email,
            "phone": cust_phone,
            "vip_tier": "Silver",
            "total_spend": 0.0,
            "points": 0,
            "created_at": now_str
        }
    
    new_spend = round(cust.get("total_spend", 0.0) + order_total, 2)
    cust["user_id"] = user_id
    cust["total_spend"] = new_spend
    cust["vip_tier"] = calculate_vip_tier(new_spend)
    cust["points"] = cust.get("points", 0) + int(order_total * 0.1)
    db_save_customer(cust)

    # 2. Create Order Record
    order_record = {
        "id": order_id,
        "orderId": order_id,
        "customerName": cust_name,
        "customerPhone": cust_phone,
        "customerEmail": cust_email,
        "items": items,
        "totalAmount": order_total,
        "couponCode": coupon_code,
        "discountSaved": discount_saved,
        "status": "Completed",
        "orderDate": now_str,
        "storeLocation": store_loc,
        "channel": body.get("channel", "Online / MCP Connector")
    }

    _orders_cache.insert(0, order_record)
    supabase_save_order(order_record)
    if db is not None:
        try:
            db.collection("orders").document(order_id).set(order_record)
        except Exception as e:
            logger.error("Firestore order save error: %s", e)

    # 3. Process Coupon Redemption if applicable
    if coupon_code:
        redemption_id = f"RED-{uuid.uuid4().hex[:6].upper()}"
        redemption_record = {
            "id": redemption_id,
            "couponCode": coupon_code,
            "customerName": cust_name,
            "customerEmail": cust_email,
            "customerPhone": cust_phone,
            "loyaltyTier": cust.get("vip_tier", "Silver"),
            "orderId": order_id,
            "orderTotal": order_total,
            "discountSaved": discount_saved,
            "redeemedAt": now_str,
            "storeLocation": store_loc
        }
        _redemptions_cache.insert(0, redemption_record)
        supabase_save_redemption(redemption_record)
        
        # Increment usage on coupon cache
        clean_code = coupon_code.replace(" ", "").upper()
        for c in _coupons_cache:
            if c.get("code", "").replace(" ", "").upper() == clean_code:
                c["usageCount"] = c.get("usageCount", 0) + 1
                if "redemptions" not in c:
                    c["redemptions"] = []
                c["redemptions"].insert(0, redemption_record)

        if db is not None:
            try:
                db.collection("redemptions").document(redemption_id).set(redemption_record)
            except Exception as e:
                logger.error("Firestore redemption save error: %s", e)

    return {"status": "ok", "order_id": order_id, "order": order_record, "customer": cust}


@app.post("/api/order")
async def place_order(body: dict[str, Any]) -> dict[str, Any]:
    logger.info("New In-Store / Portal Order received: %s", body)
    res = process_live_order(body)
    return {"status": "ok", "order_id": res["order_id"], "order": res["order"]}


@app.get("/api/orders")
async def get_orders() -> dict[str, Any]:
    """Return all orders from Firestore or in-memory cache."""
    orders = list(_orders_cache)
    if db is not None:
        try:
            docs = db.collection("orders").order_by("orderDate", direction=firestore.Query.DESCENDING).limit(50).stream()
            for d in docs:
                data = d.to_dict()
                if not any(o.get("id") == data.get("id") for o in orders):
                    orders.append(data)
        except Exception as e:
            logger.error("Firestore orders fetch error: %s", e)
    return {"success": True, "orders": orders}



@app.post("/api/redemptions")
async def create_redemption(body: dict[str, Any]) -> dict[str, Any]:
    import uuid
    coupon_code = (body.get("couponCode") or body.get("code") or "").strip().upper()
    cust_name = body.get("customerName", "Wi-Fi Guest")
    cust_phone = body.get("customerPhone", "+91 98201 00000")
    cust_email = body.get("customerEmail", f"{cust_phone}@ss-wifi.in")
    store_loc = body.get("storeLocation", "Mumbai - Malad West Flagship")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    redemption_id = f"RED-{uuid.uuid4().hex[:6].upper()}"

    redemption_record = {
        "id": redemption_id,
        "couponCode": coupon_code,
        "customerName": cust_name,
        "customerEmail": cust_email,
        "customerPhone": cust_phone,
        "loyaltyTier": "Silver",
        "orderId": f"SS-ORD-{uuid.uuid4().hex[:6].upper()}",
        "orderTotal": body.get("orderTotal", 2499.0),
        "discountSaved": body.get("discountSaved", 375.0),
        "redeemedAt": now_str,
        "storeLocation": store_loc
    }

    _redemptions_cache.insert(0, redemption_record)
    supabase_save_redemption(redemption_record)

    # Increment usage count on coupon
    clean_code = coupon_code.replace(" ", "").upper()
    for c in _coupons_cache:
        if c.get("code", "").replace(" ", "").upper() == clean_code:
            c["usageCount"] = c.get("usageCount", 0) + 1
            if "redemptions" not in c:
                c["redemptions"] = []
            c["redemptions"].insert(0, redemption_record)

    if db is not None:
        try:
            db.collection("redemptions").document(redemption_id).set(redemption_record)
        except Exception as e:
            logger.error("Firestore redemption save error: %s", e)

    return {"success": True, "status": "ok", "redemption": redemption_record}

@app.get("/api/redemptions")
async def get_redemptions() -> dict[str, Any]:
    """Return all coupon redemptions from Firestore or in-memory cache."""
    redemptions = list(_redemptions_cache)
    for c in _coupons_cache:
        for r in c.get("redemptions", []):
            if not any(x.get("id") == r.get("id") for x in redemptions):
                redemptions.append(r)

    if db is not None:
        try:
            docs = db.collection("redemptions").stream()
            for d in docs:
                data = d.to_dict()
                if not any(r.get("id") == data.get("id") for r in redemptions):
                    redemptions.append(data)
        except Exception as e:
            logger.error("Firestore redemptions fetch error: %s", e)
    return {"success": True, "redemptions": redemptions}


# ---------------------------------------------------------------------------
# MCP Endpoints (Model Context Protocol for Claude & Axionik Marketplace)
# ---------------------------------------------------------------------------

@app.post("/api/mcp/webhook")
@app.post("/mcp/messages")
@app.post("/mcp")
async def handle_mcp_request(body: dict[str, Any]) -> dict[str, Any]:
    """Handles MCP Tool Calls from Claude Connector & Axionik Marketplace (https://axionik-marketplace.vercel.app/mcp)."""
    logger.info("MCP Protocol Request received: %s", body)
    
    # Handle JSON-RPC 2.0 MCP method calls
    method = body.get("method", "")
    params = body.get("params", {})
    rpc_id = body.get("id", 1)

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "tools": [
                    {
                        "name": "create_shoppers_stop_order",
                        "description": "Places a purchase order at Shoppers Stop and updates loyalty points & dashboard.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "customerName": {"type": "string"},
                                "customerPhone": {"type": "string"},
                                "customerEmail": {"type": "string"},
                                "totalAmount": {"type": "number"},
                                "couponCode": {"type": "string"},
                                "items": {"type": "array"}
                            },
                            "required": ["customerName", "customerPhone", "totalAmount"]
                        }
                    },
                    {
                        "name": "redeem_coupon",
                        "description": "Redeems a Shoppers Stop discount coupon for a customer.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "customerPhone": {"type": "string"},
                                "couponCode": {"type": "string"},
                                "orderTotal": {"type": "number"}
                            },
                            "required": ["customerPhone", "couponCode"]
                        }
                    },
                    {
                        "name": "get_active_coupons",
                        "description": "Fetches active Shoppers Stop promo codes and vouchers.",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                ]
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name == "create_shoppers_stop_order":
            res = process_live_order(arguments)
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ Order #{res['order_id']} placed successfully! Amount: ₹{res['order']['totalAmount']}. Customer: {res['customer']['name']} ({res['customer']['vip_tier']} VIP)."
                        }
                    ]
                }
            }
        elif tool_name == "redeem_coupon":
            code = arguments.get("couponCode", "").upper()
            phone = arguments.get("customerPhone", "")
            res = process_live_order({"customerPhone": phone, "couponCode": code, "finalTotal": arguments.get("orderTotal", 1999)})
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"🎉 Coupon '{code}' redeemed successfully for {phone}! Discount applied on Order #{res['order_id']}."
                        }
                    ]
                }
            }
        elif tool_name == "get_active_coupons":
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Active Coupons: {', '.join(c['code'] for c in _coupons_cache)}"
                        }
                    ]
                }
            }

    # Standard Webhook POST fallback
    if "order" in body or "totalAmount" in body or "customerPhone" in body or "user" in body:
        res = process_live_order(body)
        return {"status": "success", "mcp_synced": True, "order_id": res["order_id"], "customer": res["customer"]}

    return {
        "jsonrpc": "2.0",
        "id": rpc_id,
        "result": {
            "status": "Shoppers Stop MCP Connector Active",
            "marketplace_url": "https://axionik-marketplace.vercel.app/mcp"
        }
    }




@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard-ui", response_class=HTMLResponse)
async def dashboard_page():
    """Renders the SHOPPERS STOP Live Dashboard UI (React App)."""
    index_file = r"c:\Users\rentk\Projects\freesalewifi\frontend\shopperstop-dashboard-app\dist\index.html"
    if os.path.isfile(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="text/html")
    return Response(content="<h1>Dashboard not found</h1>", media_type="text/html")

@app.get("/api/feedbacks")
async def get_feedbacks() -> dict[str, Any]:
    return {"success": True, "feedbacks": _feedbacks_cache}

class FeedbackPayload(BaseModel):
    customerName: str
    customerEmail: str
    customerPhone: str
    loyaltyTier: str = "Silver"
    storeLocation: str = "Mumbai - Malad West Flagship"
    category: str = "Wi-Fi & Digital Kiosk"
    rating: int = 5
    title: str
    comment: str

@app.post("/api/feedback")
async def add_feedback(body: FeedbackPayload) -> dict[str, Any]:
    item = {
        "id": f"REV-{len(_feedbacks_cache) + 1001}",
        "customerName": body.customerName,
        "customerEmail": body.customerEmail,
        "customerPhone": body.customerPhone,
        "loyaltyTier": body.loyaltyTier,
        "storeLocation": body.storeLocation,
        "category": body.category,
        "rating": body.rating,
        "title": body.title,
        "comment": body.comment,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M %p"),
        "sentiment": "Delighted" if body.rating >= 4 else "Positive",
        "verifiedPurchase": True,
        "helpfulCount": 1,
        "managerResponse": None
    }
    _feedbacks_cache.insert(0, item)

    # Sync to Firestore if ready
    if firebase_ready and db:
        try:
            db.collection("customer_feedbacks").document(item["id"]).set(item, merge=True)
            logger.info("Synced new feedback to Firestore: %s", item["id"])
        except Exception as e:
            logger.error("Firestore feedback sync error: %s", e)

    return {"status": "success", "feedback": item}

def seed_firestore_live() -> None:
    """Automatically populates initial collections into Firestore Database."""
    if not (firebase_ready and db):
        return
    try:
        # Seed Customers
        c_ref = db.collection("customers")
        c_ref.document("ananya.d@gmail.com").set({
            "id": "FC-10089",
            "username": "Ananya Deshmukh",
            "email": "ananya.d@gmail.com",
            "phone": "+91 98201 44321",
            "loyaltyTier": "Black",
            "loyaltyPoints": 18450,
            "totalSpent": 245000,
            "totalOrders": 14,
            "preferredCategory": "Ethnic & Womenswear",
            "lastVisitAt": datetime.now(timezone.utc).isoformat()
        }, merge=True)
        c_ref.document("rahul.verma@techcorp.io").set({
            "id": "FC-10090",
            "username": "Rahul Verma",
            "email": "rahul.verma@techcorp.io",
            "phone": "+91 97112 88401",
            "loyaltyTier": "Platinum",
            "loyaltyPoints": 9200,
            "totalSpent": 98500,
            "totalOrders": 8,
            "preferredCategory": "Wi-Fi & Digital Kiosk",
            "lastVisitAt": datetime.now(timezone.utc).isoformat()
        }, merge=True)

        # Seed Redemptions
        r_ref = db.collection("coupon_redemptions")
        r_ref.document("RED-101").set({
            "id": "RED-101",
            "couponCode": "FESTIVE20",
            "customerName": "Ananya Deshmukh",
            "customerEmail": "ananya.d@gmail.com",
            "customerPhone": "+91 98201 44321",
            "loyaltyTier": "Black",
            "orderId": "SS-ORD-98421",
            "orderTotal": 12999,
            "discountSaved": 2599,
            "storeLocation": "Mumbai - Malad West Flagship",
            "redeemedAt": datetime.now().strftime("%Y-%m-%d %H:%M %p")
        }, merge=True)

        # Seed Feedbacks
        f_ref = db.collection("customer_feedbacks")
        f_ref.document("REV-1001").set({
            "id": "REV-1001",
            "customerName": "Ananya Deshmukh",
            "customerEmail": "ananya.d@gmail.com",
            "customerPhone": "+91 98201 44321",
            "loyaltyTier": "Black",
            "storeLocation": "Mumbai - Malad West Flagship",
            "category": "Ethnic & Womenswear",
            "rating": 5,
            "title": "Exceptional Bridal Saree Consultation",
            "comment": "The personal shopper service in Ethnic Wear was world-class. VIP Lounge billing was seamless!",
            "sentiment": "Delighted",
            "verifiedPurchase": True,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M %p")
        }, merge=True)

        logger.info("Successfully seeded live Firestore database collections (customers, redemptions, feedbacks)!")
    except Exception as exc:
        logger.error("Firestore seeding failed: %s", exc)

# Execute seed on startup
seed_firestore_live()


# ---------------------------------------------------------------------------
# ESP32 Serial Monitor Listener Thread (PowerShell & Firebase Real-Time Sync)
# ---------------------------------------------------------------------------
import threading
import json
import time

def start_serial_monitor():
    def serial_worker():
        try:
            import serial
            import serial.tools.list_ports
        except ImportError:
            logger.warning("pyserial package not installed. Skipping hardware serial listener.")
            return

        connected_ser = None
        current_port = None

        while True:
            try:
                if connected_ser is None or not connected_ser.is_open:
                    ports = [p.device for p in serial.tools.list_ports.comports()]
                    for port in ports:
                        try:
                            ser = serial.Serial(port, 115200, timeout=1)
                            connected_ser = ser
                            current_port = port
                            logger.info("⚡ [ESP32 HARDWARE CONNECTED] Monitoring ESP32 Serial on %s at 115200 baud...", port)
                            break
                        except Exception:
                            continue

                if connected_ser and connected_ser.is_open:
                    line = connected_ser.readline().decode("utf-8", errors="ignore").strip()
                    if line:
                        if "User Data:" in line or "[LOGIN LOG]" in line or "{" in line:
                            logger.info("📡 [ESP32 SERIAL PAYLOAD] %s", line)
                            
                            # Parse JSON inside line if present
                            json_start = line.find("{")
                            json_end = line.rfind("}")
                            if json_start != -1 and json_end > json_start:
                                try:
                                    payload = json.loads(line[json_start:json_end+1])
                                    cust_name = payload.get("name") or payload.get("customerName") or "Store Shopper"
                                    cust_email = payload.get("email") or payload.get("customerEmail") or f"shopper_{int(time.time())}@shoppersstop.com"
                                    cust_phone = payload.get("phone") or payload.get("customerPhone") or "+91 98201 00000"
                                    store_loc = payload.get("storeLocation") or "Mumbai - Malad West Flagship"
                                    coupon = payload.get("coupon") or payload.get("couponCode")
                                    feedback_txt = payload.get("feedback") or payload.get("comment")

                                    print("\n==================================================================", flush=True)
                                    print(f"★ REAL-TIME ESP32 PORTAL SIGN-IN CAPTURED VIA SERIAL MONITOR ★", flush=True)
                                    print(f"Customer: {cust_name} | Phone: {cust_phone} | Email: {cust_email}", flush=True)
                                    if coupon:
                                        print(f"Coupon Redeemed: {coupon}", flush=True)
                                    if feedback_txt:
                                        print(f"Customer Feedback: {feedback_txt}", flush=True)
                                    print("==================================================================\n", flush=True)

                                    # Save to memory cache
                                    cust_obj = {
                                        "user_id": f"cust_{cust_phone.replace('+', '')}",
                                        "name": cust_name,
                                        "phone": cust_phone,
                                        "email": cust_email,
                                        "vip_tier": "Gold",
                                        "total_spend": 0.0,
                                        "created_at": datetime.now(timezone.utc).isoformat(),
                                        "last_visit": datetime.now(timezone.utc).isoformat()
                                    }
                                    db_save_customer(cust_obj)

                                    # Save to Firestore if available
                                    if firebase_ready and db:
                                        db.collection("customers").document(cust_email).set({
                                            "id": f"FC-{int(time.time())%100000}",
                                            "username": cust_name,
                                            "email": cust_email,
                                            "phone": cust_phone,
                                            "loyaltyTier": "Gold",
                                            "storeLocation": store_loc,
                                            "lastVisitAt": datetime.now(timezone.utc).isoformat()
                                        }, merge=True)

                                        if coupon:
                                            db.collection("coupon_redemptions").add({
                                                "couponCode": str(coupon).upper(),
                                                "customerName": cust_name,
                                                "customerEmail": cust_email,
                                                "customerPhone": cust_phone,
                                                "storeLocation": store_loc,
                                                "redeemedAt": datetime.now().strftime("%Y-%m-%d %H:%M %p")
                                            })

                                        if feedback_txt:
                                            db.collection("customer_feedbacks").add({
                                                "customerName": cust_name,
                                                "customerEmail": cust_email,
                                                "customerPhone": cust_phone,
                                                "storeLocation": store_loc,
                                                "rating": 5,
                                                "comment": feedback_txt,
                                                "sentiment": "Delighted",
                                                "createdAt": datetime.now(timezone.utc).isoformat()
                                            })
                                        logger.info("✓ Firestore updated with live ESP32 serial data!")
                                except Exception as parse_err:
                                    logger.debug("Serial JSON parse info: %s", parse_err)

            except Exception as e:
                connected_ser = None
                time.sleep(2)
            time.sleep(0.1)

    t = threading.Thread(target=serial_worker, daemon=True)
    t.start()

start_serial_monitor()



# Duplicate route removed — dashboard is served by dashboard_page() above


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting SHOPPERS STOP FastAPI backend on port %d", DEFAULT_PORT)
    uvicorn.run(app, host="0.0.0.0", port=DEFAULT_PORT)
