import redis
import json
import requests

r = redis.Redis(host='192.168.0.2', port=6379, decode_responses=True)

def get_available_drone():
    for key in r.keys("drone:*"):
        data = r.get(key)
        if not data:
            continue

        drone = json.loads(data)

        if drone["status"] == "idle":
            return drone

    return None

def send_mission(from_coords, area, problem=None, owner=None):
    drone = get_available_drone()

    if not drone:
        print("No drone available")
        return

    drone_ip = drone["ip"]

    # Markera som busy och koppla till användare
    drone["status"] = "busy"
    drone["owner"] = owner

    r.set(f"drone:{drone['id']}", json.dumps(drone))

    print("Sending mission to:", drone_ip, "Owner:", owner)

    try:
        requests.post(
            f"http://{drone_ip}:5000/move",
            json={
                "from": from_coords,
                "area": area,
                "problem": problem,
                "owner": owner
            },
            timeout=5
        )

    except Exception as e:
        print("Error:", e)