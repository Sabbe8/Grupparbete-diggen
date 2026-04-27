import redis
import requests
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def get_available_drone():

    for key in r.keys("drone:*"):
        drone = json.loads(r.get(key))

        if drone["status"] == "idle":
            return drone

    return None


def send_mission(from_coords, to_coords):

    drone = get_available_drone()

    if not drone:
        print("NO DRONE AVAILABLE")
        return

    ip = drone["ip"]

    url = f"http://{ip}:5000/"

    print("CONTROLLER SEND")
    print(from_coords, "→", to_coords)

    requests.post(url, json={
        "from": from_coords,
        "to": to_coords
    })
