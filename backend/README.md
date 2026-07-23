# AXIONIK Backend — Python FastAPI Server

> REST API for customer registration, orders, store menus, and analytics dashboard.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run Locally

```bash
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health check |
| `POST` | `/register-customer` | WiFi sign-in + customer registration |
| `GET` | `/api/customers` | List all customer profiles |
| `GET` | `/api/activity` | Recent check-in activity feed |
| `GET` | `/api/menu/{store_id}` | Store products and offers |
| `POST` | `/api/order` | Place a customer order |
| `GET` | `/api/order/{order_id}` | Get order details |
| `GET` | `/api/dashboard/summary` | Aggregated dashboard stats |
| `GET` | `/dashboard-ui` | Web dashboard (browser) |

## Project Structure

```
app/
├── main.py               ← FastAPI app + router wiring
├── routers/
│   ├── auth.py           ← /register-customer
│   ├── customers.py      ← /api/customers, /api/activity
│   ├── orders.py         ← /api/order
│   ├── menu.py           ← /api/menu/{store_id}
│   └── dashboard.py      ← /api/dashboard/summary
├── models/
│   ├── customer.py       ← CustomerOut Pydantic model
│   ├── order.py          ← OrderOut Pydantic model
│   └── menu_item.py      ← MenuItemOut Pydantic model
├── services/
│   ├── firebase_service.py ← Firestore CRUD + memory fallback
│   └── payment_service.py  ← Payment stub (Razorpay/Stripe)
└── utils/
    └── helpers.py        ← Store registry, VIP tier, dashboard HTML
```

## Firebase Setup

1. Create a Firebase project at https://console.firebase.google.com
2. Generate a service account key (Project Settings → Service Accounts)
3. Save it as `backend/firebase-key.json`

> ⚠️ `firebase-key.json` is gitignored. Never commit it.

## Deploy to Render

```bash
bash ../scripts/deploy.sh render
```

## Deploy with Docker

```bash
bash ../scripts/deploy.sh docker
```
