# FILE: backend/app/main.py
# DESCRIPTION: AXIONIK FastAPI backend — application entry point

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .routers import customers, orders, menu, dashboard, auth
from .services.firebase_service import firebase_ready
from .utils.helpers import get_dashboard_html

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AXIONIK API",
    description="AXIONIK client node backend services",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------------------------------------------------------------------------
# Include Routers
# ---------------------------------------------------------------------------

app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(menu.router)
app.include_router(dashboard.router)

# ---------------------------------------------------------------------------
# Core Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Returns backend service health status."""
    return {
        "status": "ok",
        "firebase_ready": firebase_ready,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/dashboard-ui")
async def dashboard_ui() -> HTMLResponse:
    """Renders the premium AXIONIK client management dashboard."""
    return HTMLResponse(get_dashboard_html())


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting AXIONIK FastAPI app on port 8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
