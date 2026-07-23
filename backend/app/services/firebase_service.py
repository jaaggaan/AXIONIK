# FILE: backend/app/services/firebase_service.py
# DESCRIPTION: Firebase Admin SDK initialization and all Firestore CRUD operations

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

FIREBASE_KEY_PATH = "firebase-key.json"

# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------

db: firestore.firestore.Client | None = None
firebase_ready = False

# Local memory cache (fallback when Firebase is unavailable)
_customers_cache: dict[str, dict[str, Any]] = {}
_visits_cache: list[dict[str, Any]] = []
_purchases_cache: dict[str, dict[str, Any]] = {}

# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

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


# Initialize on module import
init_firebase()

# ---------------------------------------------------------------------------
# Serialization Helper
# ---------------------------------------------------------------------------

def serialize_doc(data: dict[str, Any] | None) -> dict[str, Any] | None:
    """Serializes document datetimes to ISO string format."""
    if data is None:
        return None
    for key, value in list(data.items()):
        if isinstance(value, datetime):
            data[key] = value.isoformat().replace("+00:00", "Z")
    return data

# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Visits
# ---------------------------------------------------------------------------

def db_save_visit(visit_data: dict[str, Any]) -> dict[str, Any]:
    """Saves a client check-in visit to database."""
    if db is not None:
        db.collection("visits").add(visit_data)
    _visits_cache.append(visit_data)
    return visit_data


def db_list_visits() -> list[dict[str, Any]]:
    """Lists recent check-in activities."""
    if db is not None:
        docs = (
            db.collection("visits")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(100)
            .get()
        )
        return [serialize_doc(doc.to_dict() or {}) for doc in docs]
    return sorted(_visits_cache, key=lambda x: x.get("timestamp", ""), reverse=True)

# ---------------------------------------------------------------------------
# Purchases
# ---------------------------------------------------------------------------

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
