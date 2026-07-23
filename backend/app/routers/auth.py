# FILE: backend/app/routers/auth.py
# DESCRIPTION: Customer registration endpoint — WiFi sign-in flow

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from ..services.firebase_service import db_get_customer, db_save_customer, db_save_visit
from ..utils.helpers import get_store

logger = logging.getLogger(__name__)
router = APIRouter(tags=["auth"])


class RegisterCustomerRequest(BaseModel):
    name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=5)
    email: EmailStr | None = None
    store_id: str = Field(..., min_length=1)
    consent: bool = True


@router.post("/register-customer")
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
                "consent": body.consent,
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
                "consent": body.consent,
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
            "push_status": "connected",
        }
        db_save_visit(visit_data)

        return {
            "status": "success",
            "user_id": user_id,
            "customer": customer_data,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("register_customer failed: %s", exc)
        raise HTTPException(status_code=500, detail="Registration failed") from exc
