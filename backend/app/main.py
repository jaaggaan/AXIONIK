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

# ---------------------------------------------------------------------------
# Automatic USB Serial ESP32 Hardware Listener Thread
# ---------------------------------------------------------------------------

import threading
import time
import json
import re

def _start_usb_serial_listener():
    """Background thread that listens on ESP32 USB COM ports and saves sign-ins."""
    def listener_loop():
        time.sleep(2)
        try:
            import serial
            import serial.tools.list_ports
        except Exception:
            return

        from .services.firebase_service import db_save_customer, db_save_visit

        while True:
            try:
                ports = [p.device for p in serial.tools.list_ports.comports()]
                if "COM5" in ports:
                    ports.remove("COM5")
                    ports.insert(0, "COM5")
                elif any("COM" in str(p) for p in ports):
                    pass

                if not ports:
                    time.sleep(3)
                    continue

                ser = None
                for port in ports:
                    try:
                        ser = serial.Serial(port, 115200, timeout=1)
                        logger.info("🚀 USB Serial Listener successfully connected to ESP32 on %s", port)
                        break
                    except Exception as err:
                        logger.warning("Could not open serial port %s: %s", port, err)
                        continue

                if not ser:
                    time.sleep(4)
                    continue

                while ser and ser.is_open:
                    try:
                        line = ser.readline().decode("utf-8", errors="ignore")
                        if line and "{" in line and "}" in line and '"name"' in line:
                            json_part = line[line.find("{"):line.rfind("}")+1]
                            try:
                                data = json.loads(json_part)
                                name = data.get("name")
                                if name:
                                    raw_phone = data.get("phone") or "9876543210"
                                    clean_phone = re.sub(r"\D", "", raw_phone)[-10:] or "9876543210"
                                    user_id = f"wifi_{clean_phone}"
                                    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                                    db_save_customer({
                                        "user_id":      user_id,
                                        "name":         name,
                                        "phone":        f"+91{clean_phone}",
                                        "email":        data.get("email") or "",
                                        "source":       "wifi_portal",
                                        "coupon_used":  data.get("code") or "SS20",
                                        "discount_pct": data.get("discount") or 20,
                                        "total_spend":  0.0,
                                        "visit_count":  1,
                                        "vip_tier":     "Gold",
                                        "status":       "Active",
                                        "registered_at": now,
                                        "last_visit":   now.replace("T", " ")[:16],
                                        "last_seen":    now,
                                    })
                                    db_save_visit({
                                        "user_id": user_id,
                                        "name": name,
                                        "phone": f"+91{clean_phone}",
                                        "event": "WiFi Check-In",
                                        "coupon": data.get("code") or "SS20",
                                        "source": "wifi_portal",
                                        "timestamp": now,
                                    })
                                    logger.info("🚀 Real-time USB Serial sign-in synced: %s (%s)", name, user_id)
                            except Exception:
                                pass
                    except Exception:
                        if ser:
                            try:
                                ser.close()
                            except Exception:
                                pass
                        break
            except Exception:
                time.sleep(4)

    t = threading.Thread(target=listener_loop, daemon=True)
    t.start()

# _start_usb_serial_listener()

app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(menu.router)
app.include_router(dashboard.router)

# ---------------------------------------------------------------------------
# Core Endpoints & Route Aliases (with and without /api prefix)
# ---------------------------------------------------------------------------

@app.api_route("/signin", methods=["GET", "POST"])
@app.api_route("/signin/", methods=["GET", "POST"])
@app.api_route("/wifi-checkin", methods=["GET", "POST"])
@app.api_route("/wifi-checkin/", methods=["GET", "POST"])
async def root_signin_alias() -> dict[str, Any]:
    from .routers.customers import wifi_checkin, WifiCheckinPayload
    return await wifi_checkin(WifiCheckinPayload())

@app.api_route("/customers", methods=["GET"])
@app.api_route("/customers/", methods=["GET"])
async def root_customers_alias() -> list[dict[str, Any]]:
    from .routers.customers import get_customers
    return await get_customers()

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
