# FILE: backend/app/routers/menu.py
# DESCRIPTION: Store menu and product listing endpoint

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from ..utils.helpers import get_store

router = APIRouter(prefix="/api", tags=["menu"])


@router.get("/menu/{store_id}")
async def get_menu(store_id: str) -> dict[str, Any]:
    """Returns store menus and promotion details."""
    store = get_store(store_id)
    return {
        "store_id": store_id,
        "name": store["name"],
        "products": store["products"],
        "offers": store["offers"],
    }
