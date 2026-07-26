# FILE: scripts/serial_to_firebase.py
# DESCRIPTION: Live USB Serial (COM port) -> Firebase Firestore Direct Sync Bridge
# USAGE: python scripts/serial_to_firebase.py [COM_PORT]
# EXAMPLE: python scripts/serial_to_firebase.py COM3

import os
import sys
import time
import json
import re
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Auto-install dependencies
# ---------------------------------------------------------------------------
try:
    import serial
    import serial.tools.list_ports
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyserial"])
    import serial
    import serial.tools.list_ports

try:
    import firebase_admin
    from firebase_admin import credentials, firestore as fb_firestore
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "firebase-admin"])
    import firebase_admin
    from firebase_admin import credentials, firestore as fb_firestore

# ---------------------------------------------------------------------------
# Firebase Initialization (standalone, no backend dependency)
# ---------------------------------------------------------------------------

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

CANDIDATE_KEY_PATHS = [
    os.environ.get("FIREBASE_CREDENTIALS_PATH"),
    os.path.join(PROJECT_ROOT, "backend", "firebase-key.json"),
    os.path.join(PROJECT_ROOT, "firebase-key.json"),
    os.path.join(SCRIPT_DIR, "firebase-key.json"),
]

db = None

def init_firebase():
    global db
    if firebase_admin._apps:
        db = fb_firestore.client()
        return True

    for path in CANDIDATE_KEY_PATHS:
        if path and os.path.isfile(path):
            cred = credentials.Certificate(path)
            firebase_admin.initialize_app(cred)
            db = fb_firestore.client()
            print(f"[FIREBASE] Connected using key: {path}")
            return True

    print("[FIREBASE] ERROR: firebase-key.json not found!")
    print(f"  Searched: {[p for p in CANDIDATE_KEY_PATHS if p]}")
    return False


# ---------------------------------------------------------------------------
# Upload sign-in data directly to Firestore
# ---------------------------------------------------------------------------

def upload_to_firebase(json_str: str) -> None:
    """Parses sign-in payload and uploads directly to Firebase Firestore."""
    if db is None:
        print("[FIREBASE] Not connected - skipping upload")
        return
    try:
        data = json.loads(json_str)
        name = data.get("name")
        if not name:
            return

        raw_phone = data.get("phone") or "9000000000"
        clean_phone = re.sub(r"\D", "", raw_phone)[-10:] or "9000000000"
        user_id = f"wifi_{clean_phone}"
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        customer_doc = {
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
        }

        visit_doc = {
            "user_id":   user_id,
            "name":      name,
            "phone":     f"+91{clean_phone}",
            "event":     "WiFi Check-In",
            "coupon":    data.get("code") or "SS20",
            "source":    "wifi_portal",
            "timestamp": now,
        }

        # Write directly to Firestore
        db.collection("customers").document(user_id).set(customer_doc)
        db.collection("visits").add(visit_doc)

        print("")
        print("=" * 60)
        print(" [FIREBASE SYNC SUCCESS] Customer saved to Firestore!")
        print(f"   Name    : {name}")
        print(f"   Phone   : +91{clean_phone}")
        print(f"   User ID : {user_id}")
        print("=" * 60)

    except Exception as err:
        print(f"[ERROR] Failed to upload to Firebase: {err}")


# ---------------------------------------------------------------------------
# Main: Serial port listener
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  SHOPPERS STOP -- Serial -> Firebase Firestore Sync")
    print("=" * 60)

    firebase_ok = init_firebase()
    print(f"Firebase Status : {'CONNECTED (Live Firestore)' if firebase_ok else 'OFFLINE - data will NOT save'}")

    if not firebase_ok:
        print("\n[!] Cannot continue without Firebase. Check firebase-key.json location.")
        return

    target_port = sys.argv[1].upper() if len(sys.argv) > 1 else None

    ser = None
    while not ser:
        ports = [p.device for p in serial.tools.list_ports.comports()]

        if not ports:
            print("\r[WAIT] No COM ports found. Plug in ESP32 USB cable...   ", end="", flush=True)
            time.sleep(3)
            continue

        search_order = [target_port] if target_port and target_port in ports else \
                       ["COM5", "COM3", "COM4"] + [p for p in ports if p not in ["COM5", "COM3", "COM4"]]
        search_order = [p for p in search_order if p in ports]

        print(f"\r[SCAN] Trying ports: {search_order}...   ", end="", flush=True)

        for port in search_order:
            try:
                ser = serial.Serial(port, 115200, timeout=1)
                print(f"\n[SUCCESS] Connected to ESP32 on {port} at 115200 baud!")
                break
            except PermissionError:
                print(f"\n[BUSY] {port} is in use by another program. Close Arduino Serial Monitor!")
            except Exception as e:
                print(f"\n[SKIP] {port}: {e}")

        if not ser:
            print("\n[WAIT] Retrying in 3 seconds...", end="", flush=True)
            time.sleep(3)

    print("\nListening for ESP32 sign-ins... (Press Ctrl+C to stop)\n")

    while True:
        try:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if line:
                print(line)
                # Detect JSON sign-in payload
                if "{" in line and "}" in line and '"name"' in line:
                    json_part = line[line.find("{"):line.rfind("}") + 1]
                    upload_to_firebase(json_part)
        except KeyboardInterrupt:
            print("\nStopped by user.")
            break
        except Exception:
            time.sleep(0.5)

    if ser:
        ser.close()


if __name__ == "__main__":
    main()
