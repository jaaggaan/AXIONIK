# FILE: main.py
# DESCRIPTION: AXIONIK FastAPI backend & Shoppers Stop Dashboard — Firebase Firestore Sync

from __future__ import annotations

import logging
import os
import time
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
# Supabase PostgreSQL Cloud Database Service
# ---------------------------------------------------------------------------
supabase_client: Any = None
supabase_ready: bool = False

try:
    from supabase import create_client
    supa_url = "https://stnunolvbdvbhwolrnnd.supabase.co"
    supa_key = "sb_publishable_lb5pkUjGApbO0gjZDwz70w_kPLLQLxA"
    
    config_file = "supabase_config.json"
    if os.path.isfile(config_file):
        try:
            import json
            with open(config_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                if cfg.get("supabase_url"):
                    supa_url = cfg["supabase_url"]
                if cfg.get("supabase_key"):
                    supa_key = cfg["supabase_key"]
        except Exception as e:
            logger.warning("Could not parse supabase_config.json: %s", e)

    if supa_url and supa_key:
        supabase_client = create_client(supa_url, supa_key)
        supabase_ready = True
        logger.info("✅ Supabase Cloud Database connected successfully! URL: %s", supa_url)
except Exception as exc:
    logger.warning("Supabase initialization error: %s", exc)


def supabase_save_customer(cust: dict[str, Any]) -> None:
    if not (supabase_ready and supabase_client):
        return
    try:
        data = {
            "id": str(cust.get("user_id") or cust.get("id") or f"cust_{cust.get('phone', '0')}"),
            "user_id": str(cust.get("user_id") or cust.get("id") or ""),
            "name": str(cust.get("name") or cust.get("username") or "Shoppers Stop Guest"),
            "email": str(cust.get("email") or ""),
            "phone": str(cust.get("phone") or ""),
            "vip_tier": str(cust.get("vip_tier") or cust.get("loyaltyTier") or "Silver"),
            "total_spend": float(cust.get("total_spend") or cust.get("totalSpent") or 0.0),
            "points": int(cust.get("points") or cust.get("loyaltyPoints") or 500),
            "assigned_coupon": str(cust.get("assigned_coupon") or cust.get("coupon") or cust.get("coupon_code") or cust.get("couponCode") or ""),
            "created_at": str(cust.get("created_at") or datetime.now(timezone.utc).isoformat()),
            "last_visit": str(cust.get("last_visit") or datetime.now(timezone.utc).isoformat())
        }
        supabase_client.table("customers").upsert(data).execute()
        logger.info("✓ Saved customer %s (Assigned Coupon: %s) to Supabase!", data["name"], data["assigned_coupon"])
    except Exception as e:
        logger.error("Supabase customer save error: %s", e)


_supa_cust_cache: tuple[float, list[dict[str, Any]]] = (0.0, [])
_supa_red_cache: tuple[float, list[dict[str, Any]]] = (0.0, [])
_supa_cpn_cache: tuple[float, list[dict[str, Any]]] = (0.0, [])

def supabase_list_customers() -> list[dict[str, Any]]:
    global _supa_cust_cache
    if not (supabase_ready and supabase_client):
        return []
    now = time.time()
    if now - _supa_cust_cache[0] < 30.0 and _supa_cust_cache[1]:
        return _supa_cust_cache[1]
    try:
        res = supabase_client.table("customers").select("*").execute()
        if res and res.data:
            _supa_cust_cache = (now, res.data)
            return res.data
    except Exception as e:
        logger.error("Supabase customer list error: %s", e)
    return _supa_cust_cache[1]


def supabase_list_redemptions() -> list[dict[str, Any]]:
    global _supa_red_cache
    if not (supabase_ready and supabase_client):
        return []
    now = time.time()
    if now - _supa_red_cache[0] < 30.0 and _supa_red_cache[1]:
        return _supa_red_cache[1]
    try:
        res = supabase_client.table("redemptions").select("*").execute()
        if res and res.data:
            _supa_red_cache = (now, res.data)
            return res.data
    except Exception as e:
        logger.error("Supabase redemption list error: %s", e)
    return _supa_red_cache[1]


def supabase_list_coupons() -> list[dict[str, Any]]:
    global _supa_cpn_cache
    if not (supabase_ready and supabase_client):
        return []
    now = time.time()
    if now - _supa_cpn_cache[0] < 30.0 and _supa_cpn_cache[1]:
        return _supa_cpn_cache[1]
    try:
        res = supabase_client.table("coupons").select("*").execute()
        if res and res.data:
            _supa_cpn_cache = (now, res.data)
            return res.data
    except Exception as e:
        logger.error("Supabase coupon list error: %s", e)
    return _supa_cpn_cache[1]


def supabase_save_order(order: dict[str, Any]) -> None:
    if not (supabase_ready and supabase_client):
        return
    try:
        data = {
            "id": str(order.get("id") or order.get("orderId")),
            "order_id": str(order.get("orderId") or order.get("id")),
            "customer_name": str(order.get("customerName") or "Guest"),
            "customer_phone": str(order.get("customerPhone") or ""),
            "customer_email": str(order.get("customerEmail") or ""),
            "items": order.get("items") or [],
            "total_amount": float(order.get("totalAmount") or order.get("finalTotal") or 0.0),
            "coupon_code": str(order.get("couponCode") or ""),
            "discount_saved": float(order.get("discountSaved") or 0.0),
            "status": str(order.get("status") or "Completed"),
            "order_date": str(order.get("orderDate") or datetime.now(timezone.utc).isoformat()),
            "store_location": str(order.get("storeLocation") or "Mumbai - Malad West Flagship"),
            "channel": str(order.get("channel") or "In-Store / WiFi")
        }
        supabase_client.table("orders").upsert(data).execute()
        logger.info("✓ Saved order %s to Supabase!", data["order_id"])
    except Exception as e:
        logger.error("Supabase order save error: %s", e)


def supabase_save_redemption(red: dict[str, Any]) -> None:
    if not (supabase_ready and supabase_client):
        logger.warning("⚠ Supabase not ready — skipping redemption save for %s", red.get("customerName"))
        return
    import traceback
    try:
        data = {
            "id": str(red.get("id") or f"RED-{int(datetime.now().timestamp())}"),
            "coupon_code": str(red.get("couponCode") or red.get("coupon_code") or "").replace(" ", "").upper(),
            "customer_name": str(red.get("customerName") or "Guest"),
            "customer_email": str(red.get("customerEmail") or ""),
            "customer_phone": str(red.get("customerPhone") or ""),
            "loyalty_tier": str(red.get("loyaltyTier") or "Gold First Citizen"),
            "order_id": str(red.get("orderId") or ""),
            "order_total": float(red.get("orderTotal") or 0.0),
            "discount_saved": float(red.get("discountSaved") or 0.0),
            "redeemed_at": datetime.now(timezone.utc).isoformat(),
            "store_location": str(red.get("storeLocation") or "Mumbai - Malad West Flagship")
        }
        print(f"[SUPABASE] Saving redemption: {data['id']} | {data['customer_name']} | {data['coupon_code']}", flush=True)
        res = supabase_client.table("redemptions").upsert(data).execute()
        print(f"[SUPABASE] Redemption save result: {res.data}", flush=True)
        logger.info("✓ Saved redemption %s for %s (%s) to Supabase!", data["id"], data["customer_name"], data["coupon_code"])

        # Also update the coupons row: bump usage_count & append customer name
        try:
            c_code = data["coupon_code"]
            c_name = data["customer_name"]
            existing_cpn_res = supabase_client.table("coupons").select("id,code,usage_count,redeemed_customers").eq("code", c_code).execute()
            if existing_cpn_res and existing_cpn_res.data:
                curr_cpn = existing_cpn_res.data[0]
                curr_names: str = curr_cpn.get("redeemed_customers") or ""
                if c_name not in curr_names:
                    new_names = (curr_names + ", " + c_name).strip(", ")
                else:
                    new_names = curr_names
                new_usage = int(curr_cpn.get("usage_count") or 0) + 1
                patch_res = supabase_client.table("coupons").update({
                    "usage_count": new_usage,
                    "redeemed_customers": new_names
                }).eq("code", c_code).execute()
                logger.info("✓ Updated coupons[%s] usage_count=%d redeemed_customers=%s", c_code, new_usage, new_names)
            else:
                logger.warning("⚠ Coupon %s not found in Supabase — cannot update redeemed_customers", c_code)
        except Exception as cpn_err:
            logger.error("Supabase coupon update error after redemption: %s\n%s", cpn_err, traceback.format_exc())
    except Exception as e:
        print(f"[SUPABASE ERROR] Redemption save FAILED: {e}", flush=True)
        logger.error("Supabase redemption save error: %s\n%s", e, traceback.format_exc())


def supabase_list_redemptions() -> list[dict[str, Any]]:
    if not (supabase_ready and supabase_client):
        return []
    try:
        res = supabase_client.table("redemptions").select("*").execute()
        if res and res.data:
            return res.data
    except Exception as e:
        logger.error("Supabase redemption list error: %s", e)
    return []



def supabase_save_coupon(cpn: dict[str, Any]) -> None:
    if not (supabase_ready and supabase_client):
        return
    try:
        data = {
            "id": str(cpn.get("id") or f"CPN-{int(datetime.now().timestamp())}"),
            "code": str(cpn.get("code") or "").replace(" ", "").upper(),
            "title": str(cpn.get("title") or cpn.get("code") or "Coupon Offer"),
            "description": str(cpn.get("description") or "Promotional Discount"),
            "discount_type": str(cpn.get("discountType") or cpn.get("discount_type") or "Percentage"),
            "discount_value": float(cpn.get("discountValue") or cpn.get("discount_value") or 10.0),
            "min_order_value": float(cpn.get("minOrderValue") or cpn.get("min_order_value") or 1999.0),
            "usage_count": int(cpn.get("usageCount") or cpn.get("usage_count") or 0),
            "max_usage": int(cpn.get("maxUsage") or cpn.get("max_usage") or 5000),
            "status": str(cpn.get("status") or "Active"),
            "start_date": str(cpn.get("startDate") or cpn.get("start_date") or "2026-07-01"),
            "end_date": str(cpn.get("endDate") or cpn.get("end_date") or "2026-12-31"),
            "applicable_category": str(cpn.get("applicableCategory") or cpn.get("applicable_category") or "Site-wide")
        }
        supabase_client.table("coupons").upsert(data).execute()
        logger.info("✓ Saved coupon %s to Supabase!", data["code"])
    except Exception as e:
        logger.error("Supabase coupon save error: %s", e)


def supabase_list_coupons() -> list[dict[str, Any]]:
    if not (supabase_ready and supabase_client):
        return []
    try:
        res = supabase_client.table("coupons").select("*").execute()
        if res and res.data:
            return res.data
    except Exception as e:
        logger.error("Supabase coupon list error: %s", e)
    return []


def supabase_save_feedback(fb: dict[str, Any]) -> None:
    if not (supabase_ready and supabase_client):
        return
    try:
        data = {
            "id": str(fb.get("id") or f"FB-{int(datetime.now().timestamp())}"),
            "customer_name": str(fb.get("customerName") or fb.get("name") or "Guest"),
            "customer_email": str(fb.get("customerEmail") or fb.get("email") or ""),
            "customer_phone": str(fb.get("customerPhone") or fb.get("phone") or ""),
            "loyalty_tier": str(fb.get("loyaltyTier") or "Gold First Citizen"),
            "store_location": str(fb.get("storeLocation") or "Mumbai - Malad West Flagship"),
            "category": str(fb.get("category") or "General"),
            "rating": int(fb.get("rating") or 5),
            "title": str(fb.get("title") or "Store Feedback"),
            "comment": str(fb.get("comment") or fb.get("feedback") or ""),
            "date": str(fb.get("date") or datetime.now().strftime("%Y-%m-%d")),
            "time": str(fb.get("time") or datetime.now().strftime("%I:%M %p")),
            "sentiment": str(fb.get("sentiment") or "Delighted"),
            "verified_purchase": bool(fb.get("verifiedPurchase", True)),
            "helpful_count": int(fb.get("helpfulCount") or 0),
            "manager_response": str(fb.get("managerResponse") or "")
        }
        supabase_client.table("feedbacks").upsert(data).execute()
        logger.info("✓ Saved feedback %s to Supabase!", data["id"])
    except Exception as e:
        logger.error("Supabase feedback save error: %s", e)


# ---------------------------------------------------------------------------
# Database Layer (Supabase PostgreSQL + Firestore + Local Cache)
# ---------------------------------------------------------------------------

db: Any = None
firebase_ready: bool = False

_customers_cache: dict[str, dict[str, Any]] = {}
_visits_cache: list[dict[str, Any]] = []
_purchases_cache: dict[str, dict[str, Any]] = {}
_orders_cache: list[dict[str, Any]] = []
_redemptions_cache: list[dict[str, Any]] = []
_feedbacks_cache: list[dict[str, Any]] = []

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
        "redemptions": []
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
        "redemptions": []
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
    global db, firebase_ready
    try:
        if firebase_admin._apps and not force_reload:
            db = firestore.client()
            firebase_ready = True
            return
        candidate_paths = [os.environ.get("FIREBASE_CREDENTIALS_PATH", ""), "firebase-key.json", "firebasekey.json"]
        for p in candidate_paths:
            if p and os.path.isfile(p):
                cred = credentials.Certificate(p)
                firebase_admin.initialize_app(cred)
                db = firestore.client()
                firebase_ready = True
                break
    except Exception as exc:
        logger.warning("Firebase init skipped: %s", exc)

init_firebase()

# Seed initial 4 coupons to Supabase if empty
try:
    if supabase_ready and supabase_client:
        for cpn in _coupons_cache:
            supabase_save_coupon(cpn)
except Exception as _e:
    pass


def db_save_customer(customer_data: dict[str, Any]) -> dict[str, Any]:
    user_id = customer_data.get("user_id") or customer_data.get("id") or "cust_unknown"
    customer_data["user_id"] = user_id
    _customers_cache[user_id] = customer_data
    supabase_save_customer(customer_data)
    if db is not None:
        try:
            db.collection("customers").document(user_id).set(customer_data)
        except Exception as e:
            logger.error("Firestore customer save error: %s", e)
    return customer_data

def db_get_customer(user_id: str) -> dict[str, Any] | None:
    if user_id in _customers_cache:
        return _customers_cache[user_id]
    supa_custs = supabase_list_customers()
    for sc in supa_custs:
        if sc.get("user_id") == user_id or sc.get("id") == user_id:
            return sc
    return None

def db_list_customers() -> list[dict[str, Any]]:
    supa_custs = supabase_list_customers()
    if supa_custs:
        # Merge with in-memory cache
        cache_list = list(_customers_cache.values())
        for sc in supa_custs:
            uid = sc.get("user_id") or sc.get("id")
            if uid and not any(c.get("user_id") == uid for c in cache_list):
                cache_list.append(sc)
        return cache_list
    return list(_customers_cache.values())

def db_save_visit(visit_data: dict[str, Any]) -> None:
    _visits_cache.insert(0, visit_data)

def db_list_visits() -> list[dict[str, Any]]:
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
    name: str | None = "Wi-Fi Shopper"
    username: str | None = None
    phone: str | None = "+91 98201 00000"
    phnumber: str | None = None
    email: str | None = ""
    coupon: str | None = ""
    couponCode: str | None = ""
    coupon_code: str | None = ""
    sessionVoucherCode: str | None = ""
    feedback: str | None = ""

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


def verify_and_process_coupon(coupon_code: str, name: str, email: str, phone: str) -> dict[str, Any] | None:
    clean_code = (coupon_code or "").replace(" ", "").upper()
    if not clean_code:
        clean_code = "FESTIVE20"

    # Check Supabase coupons table or local cache to verify coupon existence
    valid_coupon = None
    if supabase_ready and supabase_client:
        try:
            res = supabase_client.table("coupons").select("*").eq("code", clean_code).execute()
            if res and res.data and len(res.data) > 0:
                valid_coupon = res.data[0]
        except Exception as e:
            logger.warning("Supabase coupon lookup error: %s", e)

    if not valid_coupon:
        for c in _coupons_cache:
            if c.get("code", "").replace(" ", "").upper() == clean_code:
                valid_coupon = c
                break

    if not valid_coupon:
        logger.info("ℹ Coupon code '%s' not found in database — fallback to FESTIVE20", clean_code)
        clean_code = "FESTIVE20"
        valid_coupon = _coupons_cache[0] if _coupons_cache else {"code": "FESTIVE20", "discountValue": 20, "minOrderValue": 4999}

    # Verified coupon found! Record redemption
    import uuid
    red_id = f"RED-{uuid.uuid4().hex[:6].upper()}"
    discount_val = float(valid_coupon.get("discount_value") or valid_coupon.get("discountValue") or 1000.0)
    min_order_val = float(valid_coupon.get("min_order_value") or valid_coupon.get("minOrderValue") or 4999.0)
    red_record = {
        "id": red_id,
        "couponCode": clean_code,
        "customerName": name,
        "customerEmail": email,
        "customerPhone": phone,
        "loyaltyTier": "Gold First Citizen",
        "orderId": f"SS-ORD-{uuid.uuid4().hex[:5].upper()}",
        "orderTotal": min_order_val,
        "discountSaved": discount_val,
        "redeemedAt": datetime.now(timezone.utc).isoformat(),
        "storeLocation": "Mumbai - Malad West Flagship"
    }

    if not any(r.get("customerName") == name and r.get("couponCode") == clean_code for r in _redemptions_cache):
        _redemptions_cache.insert(0, red_record)

    supabase_save_redemption(red_record)

    for c in _coupons_cache:
        if c.get("code", "").replace(" ", "").upper() == clean_code:
            c["usageCount"] = c.get("usageCount", 0) + 1
            if "redemptions" not in c:
                c["redemptions"] = []
            if not any(r.get("customerName") == name for r in c["redemptions"]):
                c["redemptions"].insert(0, red_record)

    return red_record


@app.post("/api/customers")
async def create_customer(body: dict[str, Any]) -> dict[str, Any]:
    name = body.get("name") or body.get("username") or "Wi-Fi Guest"
    phone = body.get("phone") or body.get("phnumber") or "+91 98201 00000"
    email = body.get("email") or f"{phone}@ss-wifi.in"
    raw_coupon = (body.get("coupon") or body.get("couponCode") or body.get("coupon_code") or body.get("sessionVoucherCode") or "").replace(" ", "").upper()
    if not raw_coupon:
        raw_coupon = "FESTIVE20"

    user_id = f"cust_{str(phone).replace('+', '').replace(' ', '')}"

    # Verify coupon dynamically against database
    red_record = verify_and_process_coupon(raw_coupon, name, email, phone)
    assigned_coupon = raw_coupon if red_record else "FESTIVE20"

    cust = db_get_customer(user_id)
    if not cust:
        cust = {
            "user_id": user_id,
            "customer_id": user_id,
            "name": name,
            "email": email,
            "phone": phone,
            "vip_tier": "Gold",
            "total_spend": 12500.0,
            "points": 1250,
            "assigned_coupon": assigned_coupon,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    else:
        cust["name"] = name
        cust["email"] = email or cust.get("email", "")
        if assigned_coupon:
            cust["assigned_coupon"] = assigned_coupon
    
    db_save_customer(cust)

    logger.info("✓ Processed customer check-in for %s (Coupon: %s)", name, assigned_coupon or "None")
    return {"success": True, "status": "ok", "customer": cust, "redemption": red_record}

@app.get("/api/customers")
async def get_customers() -> dict[str, Any]:
    return {"success": True, "customers": db_list_customers()}

@app.get("/api/activity")
async def get_activity() -> list[dict[str, Any]]:
    return db_list_visits()

@app.post("/api/signin")
async def api_signin(body: SigninPayload) -> dict[str, Any]:
    import uuid
    now_str = datetime.now(timezone.utc).isoformat()
    
    cust_name = body.name or body.username or "Wi-Fi Shopper"
    cust_phone = body.phone or body.phnumber or "+91 98201 00000"
    cust_email = body.email or f"shopper_{int(datetime.now().timestamp())}@shoppersstop.com"
    raw_coupon = (body.coupon or body.couponCode or body.coupon_code or body.sessionVoucherCode or "").replace(" ", "").upper()
    if not raw_coupon:
        raw_coupon = "FESTIVE20"
    feedback_text = (body.feedback or "").strip()

    # Verify coupon dynamically against database
    red_record = verify_and_process_coupon(raw_coupon, cust_name, cust_email, cust_phone)
    assigned_coupon = raw_coupon if red_record else "FESTIVE20"

    user_id = f"cust_{cust_phone.replace('+', '').replace(' ', '')}"

    existing = db_get_customer(user_id)
    if existing:
        cust = {
            **existing,
            "name": cust_name,
            "email": cust_email or existing.get("email", ""),
            "assigned_coupon": assigned_coupon or existing.get("assigned_coupon", ""),
            "last_visit": now_str
        }
    else:
        cust = {
            "user_id": user_id,
            "name": cust_name,
            "phone": cust_phone,
            "email": cust_email,
            "vip_tier": "Gold",
            "total_spend": 12500.0,
            "points": 1250,
            "assigned_coupon": assigned_coupon,
            "created_at": now_str,
            "last_visit": now_str
        }

    db_save_customer(cust)

    # Process Customer Feedback if provided via Captive Portal
    if feedback_text:
        fb_id = f"FB-{uuid.uuid4().hex[:6].upper()}"
        fb_record = {
            "id": fb_id,
            "customerName": cust_name,
            "customerEmail": cust_email,
            "customerPhone": cust_phone,
            "loyaltyTier": "Gold First Citizen",
            "storeLocation": "Mumbai - Malad West Flagship",
            "category": "Captive Portal Feedback",
            "rating": 5,
            "title": "Portal WiFi Feedback",
            "comment": feedback_text,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%I:%M %p"),
            "sentiment": "Delighted",
            "verifiedPurchase": True,
            "helpfulCount": 1,
            "managerResponse": ""
        }
        _feedbacks_cache.insert(0, fb_record)
        supabase_save_feedback(fb_record)

    print("\n==================================================================", flush=True)
    print(f"* REAL-TIME ESP32 WI-FI SIGN-IN RECEIVED VIA PORTAL *", flush=True)
    print(f"Customer: {cust_name} | Phone: {cust_phone} | Email: {cust_email} | Coupon: {coupon_code} | Feedback: {feedback_text}", flush=True)
    print("==================================================================\n", flush=True)

    if firebase_ready and db:
        try:
            db.collection("customers").document(cust_email or user_id).set({
                "id": f"FC-{int(datetime.now().timestamp())%100000}",
                "username": cust_name,
                "email": cust_email,
                "phone": cust_phone,
                "loyaltyTier": "Black",
                "lastVisitAt": now_str
            }, merge=True)
        except Exception as e:
            logger.error("Firestore Wi-Fi signin sync error: %s", e)

    visit = {
        "user_id": user_id,
        "customer_name": cust_name,
        "customer_phone": cust_phone,
        "store_id": STORE_SHOPPERS_STOP,
        "store_name": "SHOPPERS STOP Flagship",
        "platform": "ESP32_WiFi",
        "timestamp": now_str,
        "push_status": "connected"
    }
    db_save_visit(visit)

    return {"status": "success", "customer": cust, "coupon_code": coupon_code, "feedback": feedback_text}

class RedemptionPayload(BaseModel):
    couponCode: str
    customerName: str | None = "Wi-Fi Shopper"
    customerPhone: str | None = ""
    customerEmail: str | None = ""
    storeLocation: str | None = "Mumbai - Malad West Flagship"
    orderTotal: float | None = 6500.0
    discountSaved: float | None = 1500.0

@app.post("/api/redemptions")
async def create_redemption(body: RedemptionPayload) -> dict[str, Any]:
    import uuid
    red_id = f"RED-{uuid.uuid4().hex[:6].upper()}"
    clean_code = body.couponCode.replace(" ", "").upper()
    
    red_record = {
        "id": red_id,
        "couponCode": clean_code,
        "customerName": body.customerName or "Wi-Fi Shopper",
        "customerEmail": body.customerEmail or "",
        "customerPhone": body.customerPhone or "",
        "loyaltyTier": "Gold First Citizen",
        "orderId": f"SS-ORD-{uuid.uuid4().hex[:5].upper()}",
        "orderTotal": body.orderTotal or 6500.0,
        "discountSaved": body.discountSaved or (1000.0 if clean_code == "BEAUTYBUY2" else 1500.0),
        "redeemedAt": datetime.now(timezone.utc).isoformat(),
        "storeLocation": body.storeLocation or "Mumbai - Malad West Flagship"
    }

    if not any(r.get("customerName") == red_record["customerName"] and r.get("couponCode") == clean_code for r in _redemptions_cache):
        _redemptions_cache.insert(0, red_record)

    supabase_save_redemption(red_record)

    for c in _coupons_cache:
        if c.get("code", "").replace(" ", "").upper() == clean_code:
            c["usageCount"] = c.get("usageCount", 0) + 1
            if "redemptions" not in c:
                c["redemptions"] = []
            if not any(r.get("customerName") == red_record["customerName"] for r in c["redemptions"]):
                c["redemptions"].insert(0, red_record)

    logger.info("✓ Processed live coupon redemption for %s: %s", body.customerName, clean_code)
    return {"success": True, "status": "ok", "redemption": red_record}

@app.get("/api/redemptions")
async def get_redemptions() -> dict[str, Any]:
    supa_reds = supabase_list_redemptions()
    merged = list(_redemptions_cache)
    if supa_reds:
        for sr in supa_reds:
            s_id = sr.get("id")
            s_code = (sr.get("coupon_code") or "").replace(" ", "").upper()
            s_name = sr.get("customer_name") or "Wi-Fi Shopper"
            if not any(r.get("id") == s_id or (r.get("customerName") == s_name and r.get("couponCode", "").replace(" ", "").upper() == s_code) for r in merged):
                merged.append({
                    "id": s_id or f"RED-{len(merged)+1}",
                    "couponId": "CPN-101",
                    "couponCode": s_code,
                    "customerName": s_name,
                    "customerEmail": sr.get("customer_email") or "",
                    "customerPhone": sr.get("customer_phone") or "",
                    "loyaltyTier": sr.get("loyalty_tier") or "Gold First Citizen",
                    "orderId": sr.get("order_id") or "SS-ORD-98400",
                    "orderTotal": float(sr.get("order_total") or 6500.0),
                    "discountSaved": float(sr.get("discount_saved") or 1300.0),
                    "redeemedAt": sr.get("redeemed_at") or "Today",
                    "storeLocation": sr.get("store_location") or "Mumbai - Malad West Flagship"
                })
    return {"success": True, "redemptions": merged}

@app.get("/api/coupons")
async def get_coupons() -> dict[str, Any]:
    supa_cpns = supabase_list_coupons()
    merged = list(_coupons_cache)

    # Load ALL live redemptions from Supabase and join them to each coupon
    try:
        live_reds_res = supabase_client.table("redemptions").select("*").execute() if supabase_ready and supabase_client else None
        live_reds: list[dict[str, Any]] = live_reds_res.data if live_reds_res and live_reds_res.data else []
    except Exception:
        live_reds = []

    def build_redemptions_for_code(cpn_code: str) -> list[dict[str, Any]]:
        """Return all redemption records (in dashboard format) for a given coupon code."""
        result = []
        seen_ids: set[str] = set()
        # First include live Supabase rows
        for r in live_reds:
            if (r.get("coupon_code") or "").replace(" ", "").upper() == cpn_code:
                rid = r.get("id", "")
                if rid not in seen_ids:
                    seen_ids.add(rid)
                    result.append({
                        "id": rid,
                        "couponCode": r.get("coupon_code", "").upper(),
                        "customerName": r.get("customer_name") or "Guest",
                        "customerEmail": r.get("customer_email") or "",
                        "customerPhone": r.get("customer_phone") or "",
                        "loyaltyTier": r.get("loyalty_tier") or "Gold First Citizen",
                        "orderId": r.get("order_id") or "",
                        "orderTotal": float(r.get("order_total") or 0.0),
                        "discountSaved": float(r.get("discount_saved") or 0.0),
                        "redeemedAt": str(r.get("redeemed_at") or ""),
                        "storeLocation": r.get("store_location") or "Mumbai - Malad West Flagship"
                    })
        # Also include any in-memory cache records not yet in Supabase
        for r in _redemptions_cache:
            if (r.get("couponCode") or "").replace(" ", "").upper() == cpn_code:
                rid = r.get("id", "")
                if rid not in seen_ids:
                    seen_ids.add(rid)
                    result.append(r)
        return result

    if supa_cpns:
        for sc in supa_cpns:
            sc_code = (sc.get("code") or "").replace(" ", "").upper()
            idx = next((i for i, c in enumerate(merged) if c.get("code", "").replace(" ", "").upper() == sc_code), -1)
            cpn_redemptions = build_redemptions_for_code(sc_code)
            formatted = {
                "id": sc.get("id") or f"CPN-{idx+1}",
                "code": sc_code,
                "title": sc.get("title") or sc_code,
                "description": sc.get("description") or "Promotional Discount",
                "discountType": sc.get("discount_type") or "Percentage",
                "discountValue": float(sc.get("discount_value") or 10.0),
                "minOrderValue": float(sc.get("min_order_value") or 1999.0),
                "usageCount": int(sc.get("usage_count") or len(cpn_redemptions)),
                "maxUsage": int(sc.get("max_usage") or 5000),
                "status": sc.get("status") or "Active",
                "startDate": sc.get("start_date") or "2026-07-01",
                "endDate": sc.get("end_date") or "2026-12-31",
                "applicableCategory": sc.get("applicable_category") or "Site-wide",
                "redemptions": cpn_redemptions
            }
            if idx != -1:
                merged[idx] = {**merged[idx], **formatted}
            else:
                merged.append(formatted)
    else:
        # No Supabase data — still populate from in-memory cache
        for cpn in merged:
            sc_code = (cpn.get("code") or "").replace(" ", "").upper()
            cpn["redemptions"] = build_redemptions_for_code(sc_code)

    return {"success": True, "coupons": merged}

@app.post("/api/coupons")
async def create_coupon(body: CouponPayload) -> dict[str, Any]:
    c = body.dict()
    c["code"] = c["code"].upper()
    _coupons_cache.insert(0, c)
    supabase_save_coupon(c)
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
async def create_redemption(body: Any) -> dict[str, Any]:
    import uuid
    b = body if isinstance(body, dict) else (body.dict() if hasattr(body, 'dict') else dict(body))
    coupon_code = (b.get("couponCode") or b.get("code") or "").strip().upper()
    cust_name = b.get("customerName") or b.get("name") or "Wi-Fi Guest"
    cust_phone = b.get("customerPhone") or b.get("phone") or "+91 98201 00000"
    cust_email = b.get("customerEmail") or b.get("email") or f"{cust_phone}@ss-wifi.in"
    store_loc = b.get("storeLocation") or "Mumbai - Malad West Flagship"

    now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    redemption_id = f"RED-{uuid.uuid4().hex[:6].upper()}"

    redemption_record = {
        "id": redemption_id,
        "couponCode": coupon_code,
        "customerName": cust_name,
        "customerEmail": cust_email,
        "customerPhone": cust_phone,
        "loyaltyTier": "Gold First Citizen",
        "orderId": b.get("orderId") or f"SS-ORD-{uuid.uuid4().hex[:5].upper()}",
        "orderTotal": float(b.get("orderTotal") or 6500.0),
        "discountSaved": float(b.get("discountSaved") or (1000.0 if coupon_code == "BEAUTYBUY2" else 1500.0)),
        "redeemedAt": now_str,
        "storeLocation": store_loc
    }

    if not any(r.get("customerName") == cust_name and r.get("couponCode") == coupon_code for r in _redemptions_cache):
        _redemptions_cache.insert(0, redemption_record)

    supabase_save_redemption(redemption_record)

    for c in _coupons_cache:
        if c.get("code", "").replace(" ", "").upper() == coupon_code:
            c["usageCount"] = c.get("usageCount", 0) + 1
            if "redemptions" not in c:
                c["redemptions"] = []
            if not any(r.get("customerName") == cust_name for r in c["redemptions"]):
                c["redemptions"].insert(0, redemption_record)

    logger.info("✓ Processed live coupon redemption for %s: %s", cust_name, coupon_code)
    return {"success": True, "status": "ok", "redemption": redemption_record}




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

                                    # Save redemption to Supabase & memory cache
                                    coupon_code = str(coupon or "ENDOFSEASON50").replace(" ", "").upper()
                                    red_id = f"RED-{uuid.uuid4().hex[:6].upper()}"
                                    red_record = {
                                        "id": red_id,
                                        "couponCode": coupon_code,
                                        "customerName": cust_name,
                                        "customerEmail": cust_email,
                                        "customerPhone": cust_phone,
                                        "loyaltyTier": "Gold First Citizen",
                                        "orderId": f"SS-ORD-{uuid.uuid4().hex[:5].upper()}",
                                        "orderTotal": 6500.0,
                                        "discountSaved": 1000.0 if coupon_code == "BEAUTYBUY2" else 1500.0,
                                        "redeemedAt": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                                        "storeLocation": store_loc
                                    }
                                    if not any(r.get("customerName") == cust_name and r.get("couponCode") == coupon_code for r in _redemptions_cache):
                                        _redemptions_cache.insert(0, red_record)
                                    supabase_save_redemption(red_record)

                                    if feedback_txt:
                                        fb_id = f"FB-{uuid.uuid4().hex[:6].upper()}"
                                        fb_record = {
                                            "id": fb_id,
                                            "customerName": cust_name,
                                            "customerEmail": cust_email,
                                            "customerPhone": cust_phone,
                                            "loyaltyTier": "Gold First Citizen",
                                            "storeLocation": store_loc,
                                            "category": "Captive Portal Feedback",
                                            "rating": 5,
                                            "title": "Portal WiFi Feedback",
                                            "comment": feedback_txt,
                                            "date": datetime.now().strftime("%Y-%m-%d"),
                                            "time": datetime.now().strftime("%I:%M %p"),
                                            "sentiment": "Delighted",
                                            "verifiedPurchase": True,
                                            "helpfulCount": 1,
                                            "managerResponse": ""
                                        }
                                        _feedbacks_cache.insert(0, fb_record)
                                        supabase_save_feedback(fb_record)

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
                                    logger.info("✓ Supabase & Firestore updated with live ESP32 serial data for %s!", cust_name)
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
