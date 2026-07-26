# FILE: backend/app/routers/customers.py
# DESCRIPTION: Customer profile endpoints

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.firebase_service import (
    db_get_customer,
    db_list_customers,
    db_list_visits,
    db_save_customer,
    db_save_visit,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["customers"])


# ── Schema for ESP32 & Web Portal checkin payload ─────────────────────────

class WifiCheckinPayload(BaseModel):
    name: str | None = "Guest Shopper"
    phone: str | None = "9876543210"
    email: str | None = None
    coupon: str | None = None
    code: str | None = None
    discount: int | None = None
    source: str = "wifi_portal"


@router.get("/customers")
async def get_customers() -> list[dict[str, Any]]:
    """Returns registered client profiles list."""
    try:
        return db_list_customers()
    except Exception as exc:
        logger.error("get_customers failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve customers") from exc


@router.get("/activity")
@router.get("/visits")
async def get_activity() -> list[dict[str, Any]]:
    """Returns client check-in visits timeline list."""
    try:
        return db_list_visits()
    except Exception as exc:
        logger.error("get_activity failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve activities") from exc


@router.get("/customers/")
@router.post("/wifi-checkin")
@router.get("/wifi-checkin")
@router.post("/wifi-checkin/")
@router.get("/wifi-checkin/")
@router.post("/signin")
@router.get("/signin")
@router.post("/signin/")
@router.get("/signin/")
@router.post("/register-customer")
@router.get("/register-customer")
@router.post("/register-customer/")
@router.get("/register-customer/")
async def wifi_checkin(payload: WifiCheckinPayload = WifiCheckinPayload()) -> dict[str, Any]:
    """
    Receives customer sign-in registration from captive portal or ESP32.
    Creates/updates customer profile and records visit event.
    """
    try:
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        name = payload.name or "Shoppers Stop Guest"
        raw_phone = payload.phone or "9876543210"
        clean_phone = re.sub(r"\D", "", raw_phone)[-10:] or "9876543210"
        user_id = f"wifi_{clean_phone}"
        coupon_code = payload.coupon or payload.code or "SS20"

        # Merge with existing customer so total_spend / visit_count are preserved
        existing = db_get_customer(user_id) or {}
        prior_spend = float(existing.get("total_spend", 0.0))
        prior_visits = int(existing.get("visit_count", 0))
        registered_at = existing.get("registered_at") or now

        customer: dict[str, Any] = {
            "user_id":      user_id,
            "name":         name,
            "phone":        f"+91{clean_phone}",
            "email":        payload.email or existing.get("email") or "",
            "source":       "wifi_portal",
            "coupon_used":  coupon_code,
            "discount_pct": payload.discount or existing.get("discount_pct") or 20,
            "total_spend":  prior_spend,          # preserve existing spend
            "visit_count":  prior_visits + 1,      # increment visit count
            "vip_tier":     existing.get("vip_tier") or "Gold",
            "status":       "Active",
            "registered_at": registered_at,
            "last_visit":   now.replace("T", " ")[:16],
            "last_seen":    now,
        }

        # Build visit / activity document
        visit: dict[str, Any] = {
            "user_id":    user_id,
            "name":       name,
            "phone":      f"+91{clean_phone}",
            "event":      "WiFi Check-In",
            "coupon":     coupon_code,
            "source":     "wifi_portal",
            "timestamp":  now,
        }

        db_save_customer(customer)
        db_save_visit(visit)

        logger.info("WiFi checkin recorded: %s (%s)", name, user_id)
        return {"status": "ok", "user_id": user_id, "message": "Welcome to Shoppers Stop!"}

    except Exception as exc:
        logger.error("wifi_checkin failed: %s", exc)
        raise HTTPException(status_code=500, detail="Checkin failed") from exc


class CouponClaimPayload(BaseModel):
    phone: str | None = None
    code: str = "SS-VIP25"
    status: str = "utilized"


@router.post("/coupon-claimed")
async def claim_coupon(payload: CouponClaimPayload) -> dict[str, Any]:
    """Records coupon copying / utilization event from captive portal."""
    try:
        from ..services.firebase_service import db_save_coupon_claim
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            "phone": payload.phone or "Anonymous",
            "code": payload.code,
            "status": payload.status,
            "timestamp": now,
        }
        db_save_coupon_claim(doc)
        return {"status": "ok", "message": "Coupon claim logged"}
    except Exception as exc:
        logger.error("claim_coupon failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to record coupon claim") from exc


class FeedbackPayload(BaseModel):
    phone: str | None = None
    rating: str  # 'like' or 'dislike'
    comment: str | None = None
    timestamp: str | None = None


@router.post("/feedback")
async def submit_feedback(payload: FeedbackPayload) -> dict[str, Any]:
    """Records store/Wi-Fi feedback rating (Like/Dislike) and comment."""
    try:
        from ..services.firebase_service import db_save_feedback
        now = payload.timestamp or datetime.now(timezone.utc).isoformat()
        doc = {
            "phone": payload.phone or "Anonymous",
            "rating": payload.rating,
            "comment": payload.comment or "",
            "timestamp": now,
        }
        db_save_feedback(doc)
        return {"status": "ok", "message": "Feedback submitted successfully"}
    except Exception as exc:
        logger.error("submit_feedback failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to submit feedback") from exc


