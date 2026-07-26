# FILE: backend/app/routers/dashboard.py
# DESCRIPTION: Dashboard analytics stub router (for future extension)

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from ..services.firebase_service import (
    db_list_coupons,
    db_list_customers,
    db_list_feedback,
    db_list_visits,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
async def dashboard_summary() -> dict[str, Any]:
    """Returns aggregated dashboard summary statistics."""
    customers = db_list_customers()
    visits = db_list_visits()
    coupons = db_list_coupons()
    feedbacks = db_list_feedback()

    total_spend = sum(c.get("total_spend", 0.0) for c in customers)
    distributed_coupons = len(customers)
    utilized_coupons = len(coupons)

    likes = sum(1 for f in feedbacks if f.get("rating") == "like")
    dislikes = sum(1 for f in feedbacks if f.get("rating") == "dislike")

    return {
        "total_customers": len(customers),
        "total_visits": len(visits),
        "total_revenue": round(total_spend, 2),
        "distributed_coupons": distributed_coupons,
        "utilized_coupons": utilized_coupons,
        "feedback_likes": likes,
        "feedback_dislikes": dislikes,
        "feedbacks": feedbacks,
    }

