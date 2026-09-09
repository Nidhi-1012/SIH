import time
import json
import urllib.request
from datetime import datetime

def run_telemetry_simulator(steps=10, delay_sec=1):
    """
    Simulates vehicle movement along NH-6 corridor (Guwahati -> Shillong -> Silchar),
    posting live telemetry coordinates to the FastAPI ingestion endpoint.
    """
    print("=== Starting Vehicle Telemetry Simulator (Guwahati -> Shillong) ===")
    
    # Waypoints along Guwahati - Shillong - Silchar arterial corridor
    waypoints = [
        (26.1445, 91.7362, "Guwahati Logistics Hub"),
        (26.1158, 91.8210, "Khanapara Junction"),
        (25.9001, 91.8805, "Nongpoh Checkpost"),
        (25.6542, 91.9056, "Umiam Lake Pass"),
        (25.5788, 91.8933, "Shillong Relief Hub"),
        (25.4485, 92.2030, "Jowai Transit Node"),
        (25.1166, 92.3551, "Sonapur Tunnel Entry"),
        (24.8333, 92.7789, "Silchar Distribution Depot")
    ]

    for i in range(min(steps, len(waypoints))):
        lat, lon, label = waypoints[i]
        payload = {
            "vehicle_id": "VEH-MED-01",
            "shipment_id": "SHIP-P0-VACCINES-901",
            "lat": lat,
            "lon": lon,
            "speed_kmh": 44.5 + (i % 5),
            "heading": 172.0,
            "cargo": "P0 Emergency Medicines (Vaccines)",
            "is_simulated": True
        }

        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request('http://127.0.0.1:8000/api/v1/telemetry', data=data, headers={'Content-Type': 'application/json'})
            res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
            print(f"Step {i+1}/{len(waypoints)}: {label} ({lat}, {lon}) -> Speed: {payload['speed_kmh']} km/h | Status: {res.get('status', 'OK')}")
        except Exception as e:
            print(f"Step {i+1}: Local server fallback ({label}) - {e}")

        time.sleep(delay_sec)

    print("\nSimulator run complete!")

if __name__ == "__main__":
    run_telemetry_simulator(steps=5, delay_sec=0.5)
