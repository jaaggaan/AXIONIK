# AXIONIK Technical Architecture

> See `axionik_technical_architecture.docx` for the full diagrams and visual architecture document.

## System Overview

```
[Customer's Phone]
      │  connects to
      ▼
[ESP32 Access Point]  ──────────────────────────────────────────────────────────────────
      │  captive portal (HTML served from firmware)                                    │
      │  POST /register-customer                                                       │
      ▼                                                                                │
[AXIONIK Backend API]  (FastAPI on Render.com)                                        │
      │  saves to                                                                       │
      ▼                                                                                │
[Firestore Database]                                                                   │
      │  read by                                                                       │
      ▼                                                                                │
[Flutter Mobile App]  ←──────── [FCM Push Notifications] ──────────────────────────────
      │  reads from
      ▼
[Dashboard UI]  (served at /dashboard-ui by backend)
```

## Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.11, FastAPI, Uvicorn |
| Database | Google Firestore (with memory fallback) |
| Mobile App | Flutter 3.x, Riverpod, FCM |
| Firmware | Arduino ESP32, WebServer, DNSServer |
| Deployment | Render.com (backend), Docker-ready |

## Data Flow

1. Customer walks into store → connects to `AXIONIK` WiFi SSID
2. Captive portal served from ESP32 → customer fills sign-in form
3. Form submitted to backend `POST /register-customer`
4. Backend saves customer profile + visit log to Firestore
5. FCM push notification sent to customer's Flutter app (if installed)
6. Store dashboard at `/dashboard-ui` updates in real time
