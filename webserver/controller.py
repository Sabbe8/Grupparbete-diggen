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

def send_mission(from_coords, to_coords):
    drone = get_available_drone()
    if not drone:
        print("No drone available")
        return

    drone_ip = drone["ip"]

    # Markera som busy
    drone["status"] = "busy"
    r.set(f"drone:{drone['id']}", json.dumps(drone))

    print("Sending mission to:", drone_ip)

    try:
        requests.post(
            f"http://{drone_ip}:5000/move",
            json={"from": from_coords, "to": to_coords},
            timeout=5
        )
    except Exception as e:
        print("Error:", e)
