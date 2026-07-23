# FILE: backend/app/models/menu_item.py
# DESCRIPTION: Menu item Pydantic models

from __future__ import annotations

from pydantic import BaseModel


class MenuItemOut(BaseModel):
    store_id: str
    name: str
    products: list[str]
    offers: list[str]
