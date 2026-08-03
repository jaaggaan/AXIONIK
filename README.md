# AXIONIK — Shoppers Stop Smart WiFi Retail System

> **AI-powered in-store WiFi captive portal + Executive Retail Intelligence Dashboard for Shoppers Stop flagship stores.**

Built by **AXIONIK** — transforming brick-and-mortar retail with smart WiFi analytics, real-time CRM, and live store intelligence.

---

## 🏗️ Project Structure

```
AXIONIK-SHOP-MODEL/
├── backend/                        ← Production FastAPI server (Dockerized, Render deploy)
│   ├── app/
│   │   ├── routers/                ← API route handlers
│   │   ├── services/               ← Firebase & payment services
│   │   ├── models/                 ← Pydantic data models
│   │   └── utils/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── render.yaml                 ← Render.com deployment config
│
├── frontend/
│   ├── captive-portal-app/         ← WiFi captive portal (React + Vite)
│   │   └── src/components/         ← VoucherModal, ScratchCard, ReviewModal, etc.
│   └── shopperstop-dashboard-app/  ← Executive Dashboard (React + Vite + Recharts)
│       └── src/components/         ← OverviewTab, CouponsTab, CustomersTab, FeedbackTab...
│
├── firmware/
│   └── esp32_captive_portal/       ← Arduino ESP32 firmware (.ino + headers)
│       ├── esp32_captive_portal.ino
│       ├── portal_html.h           ← Inlined captive portal HTML
│       └── image.h                 ← Inlined brand logo
│
├── docs/
│   ├── database_schema.sql         ← Firestore + SQL schema reference
│   ├── firebase_config.js          ← Firebase project config
│   └── axionik_shopperstop_documentation.html
│
├── scripts/
│   ├── serial_to_firebase.py       ← ESP32 serial → Firebase bridge
│   ├── bundle_portal.py            ← Build portal HTML into firmware header
│   ├── create_image_h.py           ← Convert logo PNG → image.h
│   └── update_offline_images.py
│
├── main.py                         ← Local dev server (FastAPI, port 63265)
├── firebase-key.json               ← 🔒 Firebase Admin SDK key (git-ignored in production)
└── README.md
```

---

## 🚀 How It Works

```
Customer enters store
       ↓
Connects to Shoppers Stop WiFi (ESP32 AP)
       ↓
Captive portal opens → Enter phone / name
       ↓
Firebase Firestore ← real-time CRM sync
       ↓
Voucher / scratch card / loyalty points issued
       ↓
Store Manager Dashboard ← live analytics
```

---

## 🖥️ Local Development

### Run the backend server
```powershell
cd C:\path\to\AXIONIK-SHOP-MODEL
python -m uvicorn main:app --host 0.0.0.0 --port 63265
```

Dashboard: **http://localhost:63265/**

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Executive Dashboard UI |
| GET | `/api/customers` | All registered customers |
| GET | `/api/redemptions` | Coupon redemptions from Firestore |
| GET | `/api/coupons` | Active coupons |
| POST | `/api/coupons` | Create new coupon |
| POST | `/api/signin` | WiFi portal sign-in |
| GET | `/api/feedbacks` | Customer feedback / ratings |
| POST | `/api/feedback` | Submit feedback |
| GET | `/api/activity` | Recent activity log |
| GET | `/health` | Server health check |

### Build the Dashboard React App
```powershell
cd frontend/shopperstop-dashboard-app
npm install
npm run build
```

### Flash ESP32 Firmware
1. Open `firmware/esp32_captive_portal/esp32_captive_portal.ino` in Arduino IDE
2. Install libraries: `ESP32`, `ESPAsyncWebServer`, `ArduinoJson`
3. Flash to ESP32

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Firmware** | C++ / Arduino (ESP32) |
| **Backend** | Python / FastAPI / Firebase Admin SDK |
| **Database** | Google Firestore |
| **Dashboard** | React + TypeScript + Vite + Recharts + TailwindCSS |
| **Captive Portal** | React + TypeScript + Vite |
| **Deploy** | Docker + Render.com |

---

## 🔒 Environment Setup

Copy `firebase-key.json.example` → `firebase-key.json` and fill in your Firebase credentials.

```bash
cp backend/firebase-key.json.example firebase-key.json
```

---

*Built with ❤️ by AXIONIK for Shoppers Stop — Smart Retail Intelligence*
