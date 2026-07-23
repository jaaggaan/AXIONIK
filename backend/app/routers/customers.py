# FILE: backend/app/routers/customers.py
# DESCRIPTION: Customer profile endpoints

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from ..services.firebase_service import db_list_customers

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["customers"])


@router.get("/customers")
async def get_customers() -> list[dict[str, Any]]:
    """Returns registered client profiles list."""
    try:
        return db_list_customers()
    except Exception as exc:
        logger.error("get_customers failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve customers") from exc


@router.get("/activity")
async def get_activity() -> list[dict[str, Any]]:
    """Returns client check-in visits timeline list."""
    from ..services.firebase_service import db_list_visits
    try:
        return db_list_visits()
    except Exception as exc:
        logger.error("get_activity failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve activities") from exc
