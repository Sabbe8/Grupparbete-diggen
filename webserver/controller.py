import redis
import requests
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_available_drone():
    keys = r.keys("drone:*")

    for key in keys:
        drone = json.loads(r.get(key))

        print("Checking drone:", drone)

        if drone["status"] == "idle":
            return drone

    return None


def send_mission(from_coords, to_coords):

    drone = get_available_drone()

    if not drone:
        return "No available drone, try later"

    ip = drone["ip"]

    url = f"http://{ip}:5000/"

    print(f"Sending mission to drone {drone['id']} at {ip}")

    try:
        requests.post(url, json={
            "from": from_coords,
            "to": to_coords
        })
    except Exception as e:
        print("Error:", e)
        return "Failed to send request"

    return "Got address and sent request to the drone"