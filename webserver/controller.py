import requests
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def get_available_drone():

    for key in r.keys("drone:*"):
        data = r.get(key)

        if not data:
            continue

        drone = json.loads(data)

        if drone.get("status") == "idle":
            return drone

    return None


def send_mission(from_coords, to_coords):

    drone = get_available_drone()

    if not drone:
        print("No drone available")
        return

    ip = drone.get("ip", "").replace("!", "")

    # 🧠 simulator-mode (ingen riktig drone)
    if not ip:
        print("Simulator drone, skipping HTTP request")
        return

    # sätt busy
    drone["status"] = "busy"
    r.set(f"drone:{drone['id']}", json.dumps(drone))

    url = f"http://{ip}:5000/"

    print(f"Sending mission to {url}")

    try:
        requests.post(url, json={
            "from": from_coords,
            "to": to_coords
        }, timeout=3)

    except Exception as e:
        print("Error sending mission:", e)
