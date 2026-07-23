# FILE: backend/app/models/order.py
# DESCRIPTION: Order Pydantic models

from __future__ import annotations

from pydantic import BaseModel


class OrderOut(BaseModel):
    id: str
    user_id: str
    store_id: str
    store_name: str
    product: str
    amount: float
    category: str
    timestamp: str
