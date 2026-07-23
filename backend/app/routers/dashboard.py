# FILE: backend/app/routers/dashboard.py
# DESCRIPTION: Dashboard analytics stub router (for future extension)

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from ..services.firebase_service import db_list_customers, db_list_visits

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
async def dashboard_summary() -> dict[str, Any]:
    """Returns aggregated dashboard summary statistics."""
    customers = db_list_customers()
    visits = db_list_visits()

    total_spend = sum(c.get("total_spend", 0.0) for c in customers)
    connected = sum(1 for v in visits if v.get("push_status") == "connected")
    rate = round((connected / len(visits) * 100), 1) if visits else 0.0

    return {
        "total_customers": len(customers),
        "total_visits": len(visits),
        "total_revenue": round(total_spend, 2),
        "conversion_rate": rate,
    }
