# FILE: backend/app/routers/orders.py
# DESCRIPTION: Order placement and retrieval endpoints

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.firebase_service import db_get_customer, db_get_purchase, db_save_customer, db_save_purchase
from ..utils.helpers import calculate_vip_tier, get_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["orders"])


class OrderRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    store_id: str = Field(..., min_length=1)
    product: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1)


@router.post("/order")
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
            "timestamp": now_str,
        }
        db_save_purchase(purchase_data)

        new_spend = round(customer.get("total_spend", 0.0) + body.amount, 2)
        new_tier = calculate_vip_tier(new_spend)

        updated_customer = {
            **customer,
            "total_spend": new_spend,
            "vip_tier": new_tier,
            "last_visit": now_str,
        }
        db_save_customer(updated_customer)

        return {
            "status": "success",
            "order_id": order_id,
            "purchase": purchase_data,
            "new_spend": new_spend,
            "vip_tier": new_tier,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("place_order failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to place order") from exc


@router.get("/order/{order_id}")
async def get_order(order_id: str) -> dict[str, Any]:
    """Retrieves specific order transaction details."""
    purchase = db_get_purchase(order_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Order record not found")
    return purchase
