# AXIONIK — Retail Intelligence Platform

> Seamless in-store WiFi monetization — connect customers, serve experiences, capture data.

---

## Project Structure

```
freesalewifi/
├── frontend/          ← Flutter mobile app (iOS + Android)
├── backend/           ← Python FastAPI server (Firestore + REST API)
├── firmware/          ← ESP32 Arduino captive portal sketches
├── docs/              ← Architecture, manuals, brand kits
└── scripts/           ← Automation scripts (setup, deploy)
```

---

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/jaaggaan/AXIONIK.git
cd freesalewifi
bash scripts/setup.sh
```

### 2. Run Backend

```bash
cd backend
source .venv/bin/activate       # Windows: .venv\Scripts\activate
uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/dashboard-ui
```

### 3. Run Frontend

```bash
cd frontend
flutter pub get
flutter run
```

### 4. Flash Firmware

Open `firmware/esp32_captive_portal/esp32_captive_portal.ino` in Arduino IDE and flash to your ESP32.

---

## Components

### 🖥️ Backend (`backend/`)

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app entry point |
| `app/routers/auth.py` | `/register-customer` — WiFi sign-in |
| `app/routers/customers.py` | `/api/customers`, `/api/activity` |
| `app/routers/orders.py` | `/api/order` — order placement |
| `app/routers/menu.py` | `/api/menu/{store_id}` |
| `app/routers/dashboard.py` | `/api/dashboard/summary` |
| `app/services/firebase_service.py` | Firestore CRUD + memory fallback |
| `app/utils/helpers.py` | Store registry, VIP tier logic, dashboard HTML |

### 📱 Frontend (`frontend/`)

Flutter mobile app with:
- Riverpod state management
- FCM push notifications
- Geofence-based auto-connect
- In-store onboarding flow

### 📡 Firmware (`firmware/`)

ESP32 Arduino sketches serving captive portals:
- `esp32_captive_portal/` — CRAV BISTRO food ordering portal
- `shared/common_utils.h` — shared constants & helpers

---

## Deployment

```bash
# Deploy backend to Render.com
bash scripts/deploy.sh render

# Deploy with Docker
bash scripts/deploy.sh docker
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FIREBASE_CREDENTIALS_PATH` | `firebase-key.json` | Path to Firebase service account key |

> ⚠️ **Never commit `firebase-key.json` to git.** It is in `.gitignore`.

---

## License

© 2026 AXIONIK. All rights reserved.
