import redis
import requests
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


# ================================
# Hitta ledig drönare
# ================================
def get_available_drone():
    keys = r.keys("drone:*")

    print("All drones:", keys)

    for key in keys:
        data = r.get(key)

        if not data:
            continue

        drone = json.loads(data)

        print("Checking drone:", drone)

        if drone.get("status") == "idle":
            return drone

    return None


# ================================
# Skicka uppdrag
# ================================
def send_mission(from_coords, to_coords):

    drone = get_available_drone()

    if not drone:
        print("No available drone")
        return "No available drone"

    ip = drone.get("ip")

    if not ip:
        print("ERROR: Drone missing IP:", drone)
        return "Drone missing IP"

    url = f"http://{ip}:5000/"

    payload = {
        "from": from_coords,
        "to": to_coords
    }

    print(f"Sending mission to drone {drone.get('id')} at {ip}")
    print("Payload:", payload)

    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("Error sending to drone:", e)
        return "Failed to send request"

    return "Mission sent"
