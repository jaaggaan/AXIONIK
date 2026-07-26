# FILE: scripts/serial_bridge.py
# DESCRIPTION: Listens to ESP32 USB Serial COM ports and automatically forwards guest sign-ins to local FastAPI dashboard

import sys
import time
import json
import re
import urllib.request

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Installing pyserial...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyserial"])
    import serial
    import serial.tools.list_ports

BACKEND_URL = "http://127.0.0.1:63265/api/signin"

def post_to_dashboard(json_str: str):
    """Sends JSON signin data to FastAPI backend."""
    try:
        data = json.loads(json_str)
        name = data.get("name")
        phone = data.get("phone")
        if name:
            print(f"\n[USB BRIDGE] 🚀 New Sign-In Received via USB: {name} ({phone})")
            req = urllib.request.Request(
                BACKEND_URL,
                data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                print(f"[USB BRIDGE] ✅ Successfully synced to Admin Dashboard! (Status {resp.status})")
    except Exception as err:
        name_match = re.search(r'"name"\s*:\s*"([^"]+)"', json_str)
        phone_match = re.search(r'"phone"\s*:\s*"([^"]+)"', json_str)
        if name_match:
            name = name_match.group(1)
            phone = phone_match.group(1) if phone_match else "9876543210"
            print(f"\n[USB BRIDGE] 🚀 New Sign-In Received via USB: {name} ({phone})")
            payload = {"name": name, "phone": phone, "source": "wifi_portal", "code": "SS20", "discount": 20}
            req = urllib.request.Request(
                BACKEND_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=3) as resp:
                    print(f"[USB BRIDGE] ✅ Successfully synced to Admin Dashboard! (Status {resp.status})")
            except Exception as e:
                print(f"[USB BRIDGE] Sync error: {e}")

def main():
    print("=" * 60)
    print("  SHOPPERS STOP — ESP32 USB Serial -> Dashboard Bridge")
    print("=" * 60)
    
    ports = [p.device for p in serial.tools.list_ports.comports()]
    if "COM5" in ports:
        ports.remove("COM5")
        ports.insert(0, "COM5")

    print(f"Detected Serial COM Ports: {ports}")
    
    if not ports:
        print("No COM ports found! Ensure ESP32 is plugged in via USB cable.")
        return

    ser = None
    for port in ports:
        try:
            ser = serial.Serial(port, 115200, timeout=1)
            print(f"Connected to ESP32 on {port} at 115200 baud!")
            break
        except Exception as e:
            print(f"Could not open {port}: {e}")

    if not ser:
        print("Failed to open any COM port. Ensure Arduino Serial Monitor is closed.")
        return

    print("\nListening for live ESP32 captive portal sign-ins over USB... (Press Ctrl+C to stop)\n")

    while True:
        try:
            line = ser.readline().decode("utf-8", errors="ignore")
            if line:
                sys.stdout.write(line)
                sys.stdout.flush()
                if "{" in line and "}" in line and '"name"' in line:
                    json_part = line[line.find("{"):line.rfind("}")+1]
                    post_to_dashboard(json_part)
        except KeyboardInterrupt:
            print("\nStopping USB bridge.")
            break
        except Exception:
            time.sleep(0.5)

if __name__ == "__main__":
    main()
