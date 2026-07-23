# FILE: backend/app/models/customer.py
# DESCRIPTION: Customer Pydantic models

from __future__ import annotations

from pydantic import BaseModel, EmailStr


class CustomerOut(BaseModel):
    user_id: str
    name: str
    phone: str
    email: str | None = None
    vip_tier: str = "Bronze"
    total_spend: float = 0.0
    created_at: str
    last_visit: str
    consent: bool = True
