import redis
import requests
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def get_available_drone():
    keys = r.keys("drone:*")

    for key in keys:
        drone = json.loads(r.get(key))

        print("CONTROLLER CHECK:", drone)

        if drone.get("status") == "idle":
            return drone

    return None


def send_mission(from_coords, to_coords):

    drone = get_available_drone()

    if not drone:
        print("NO DRONE AVAILABLE")
        return

    ip = drone.get("ip")

    if not ip:
        print("DRONE HAS NO IP:", drone)
        return

    url = f"http://{ip}:5000/"

    print("CONTROLLER SEND")
    print("TO DRONE:", ip)
    print("FROM:", from_coords)
    print("TO:", to_coords)

    try:
        requests.post(url, json={
            "from": from_coords,
            "to": to_coords
        })
    except Exception as e:
        print("ERROR:", e)
