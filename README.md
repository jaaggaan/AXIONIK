# ⚡ AXIONIK — Proximity Retail & Captive Portal Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB.svg?style=flat&logo=python)](https://www.python.org/)
[![ESP32](https://img.shields.io/badge/Hardware-ESP32%20Arduino-E7352C.svg?style=flat&logo=espressif)](https://www.espressif.com/)
[![Firebase](https://img.shields.io/badge/Database-Firebase%20Firestore-FFCA28.svg?style=flat&logo=firebase)](https://firebase.google.com/)

**AXIONIK** is an end-to-end proximity retail intelligence platform and WiFi captive portal system. It bridges physical ESP32 wireless microcontrollers serving guest access portals with an asynchronous Python FastAPI backend, synchronized real-time cloud database (Firebase Firestore / local fallback), and a sleek dark-glassmorphism administration dashboard.

---

## 📐 System Architecture

```
                       ┌─────────────────────────┐
                       │  ESP32 Access Point     │
                       │   (SSID: FreeSaleWiFi)  │
                       └───────────┬─────────────┘
                                   │ DNS Redirection (Port 53)
                                   ▼
                       ┌─────────────────────────┐
                       │  AXIONIK Captive Portal │
                       │    (Guest Sign-In /     │
                       │   Menu / Order Page)    │
                       └───────────┬─────────────┘
                                   │ HTTP POST /register-customer
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        AXIONIK FastAPI Backend                         │
│                                                                        │
│   ┌───────────────────────┐                 ┌──────────────────────┐   │
│   │ REST API Controller   │ ◄─────────────► │ Database Sync Layer  │   │
│   └───────────┬───────────┘                 └──────────┬───────────┘   │
│               │                                        │               │
└───────────────┼────────────────────────────────────────┼───────────────┘
                │                                        │
                ▼                                        ▼
    ┌──────────────────────┐                 ┌──────────────────────┐
    │  AXIONIK Dashboard   │                 │ Firebase Firestore / │
    │   (/dashboard-ui)    │                 │ Local Memory Cache   │
    └──────────────────────┘                 └──────────────────────┘
```

---

## 🛠️ Technical Specifications & Tech Stack

### 1. Backend Layer (Python & FastAPI)
- **Framework:** FastAPI `0.115.6` running on Uvicorn `0.34.0`.
- **Validation Engine:** Pydantic v2 with `EmailStr` and custom type constraints.
- **Database Architecture:** Firebase Admin SDK `6.6.0` with Firestore cloud persistence and thread-safe in-memory caching fallback for offline/demo operations.
- **CORS Middleware:** Configured for cross-origin access across client terminals.

### 2. Microcontroller / Hardware Layer (ESP32)
- **Microcontroller:** ESP32 (WROOM-32 / ESP32-S series).
- **Core Framework:** Arduino C++ using `WiFi.h`, `DNSServer.h`, `AsyncTCP.h`, and `ESPAsyncWebServer.h`.
- **SoftAP Configuration:** IP `192.168.4.1` / Subnet `255.255.255.0` on open network `FreeSaleWiFi`.
- **DNS Server:** Port 53 wildcard redirection (`* -> 192.168.4.1`) capturing captive portal detection probes across iOS/Apple (`hotspot-detect.html`), Android (`generate_204`), and Windows (`ncsi.txt`).
- **UI Storage:** PROGMEM embedded responsive dark glassmorphism web client with localStorage session caching.

### 3. Frontend Dashboard Layer (`/dashboard-ui`)
- **Design System:** Custom Dark Glassmorphism UI using HSL CSS tokens, backdrop filters, and responsive bento grid structure.
- **Real-Time Telemetry:** Auto-refresh polling (5s interval) fetching live metrics:
  - Total Registered Customers
  - Active WiFi Sessions (30-min window)
  - Connection & Funnel Conversion Rates
  - Gross Daily LTV Revenue
- **Components:** Filterable customer ledger, live check-in feed timeline, and slide-in customer dossier modals.

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description | Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Server health & Firebase status | N/A |
| `POST` | `/register-customer` | Register new guest / record check-in | `{ name, phone, email, store_id, consent }` |
| `GET` | `/api/customers` | Fetch all registered client profiles | N/A |
| `GET` | `/api/activity` | Fetch recent visit check-in log | N/A |
| `GET` | `/api/menu/{store_id}` | Fetch store products & promotional deals | Store ID (`store_001`, `store_002`, etc.) |
| `POST` | `/api/order` | Record store purchase & calculate VIP tier | `{ user_id, store_id, product, amount, category }` |
| `GET` | `/api/order/{order_id}`| Get transaction details by order ID | Order ID string |
| `GET` | `/dashboard-ui` | Render client management dashboard | N/A |

---

## 📋 Installation & Setup Instructions

### Prerequisites
- **Python 3.10+** (Python 3.13 recommended)
- **Arduino IDE 2.x** with ESP32 board support installed
- **Git**

### Step 1: Clone Repository
```bash
git clone https://github.com/jaaggaan/AXIONIK.git
cd AXIONIK
```

### Step 2: Set Up Python Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate on Linux / macOS
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Firebase (Optional)
Place your Firebase Admin SDK service account key file in the root directory named `firebase-key.json`. 
> *Note: If no key file is provided, AXIONIK automatically boots with an in-memory fallback database pre-seeded with demo telemetry data.*

### Step 5: Start Backend Server
```bash
python main.py
# Or run with Uvicorn directly:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Access the dashboard at: **`http://localhost:8000/dashboard-ui`**

---

## 📟 ESP32 Firmware Flashing Instructions

1. Open `esp32_captive_portal/esp32_captive_portal.ino` in **Arduino IDE**.
2. Install required libraries via Library Manager:
   - `AsyncTCP`
   - `ESPAsyncWebServer`
3. Select board: **ESP32 Dev Module**.
4. Connect ESP32 via USB and select the correct COM port.
5. Click **Upload** (`Ctrl + U`).
6. Open Serial Monitor at **115200 baud** to view SoftAP IP address and live connection logs.

---

## 👑 Customer VIP Tiers Logic

| Tier Level | Total Lifetime Spend | Badge Color |
| :--- | :--- | :--- |
| **Bronze** | `$0.00` – `$199.99` | Orange (`#fb923c`) |
| **Silver** | `$200.00` – `$499.99` | Slate (`#cbd5e1`) |
| **Gold** | `$500.00` – `$999.99` | Gold (`#fbbf24`) |
| **Platinum** | `$1000.00+` | Purple (`#c084fc`) |

---

## 📄 License

AXIONIK is distributed under the MIT License.
