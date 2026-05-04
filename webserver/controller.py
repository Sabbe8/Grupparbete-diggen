import redis
import json
import threading
from simulator import fly_to

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

    drone_id = drone["id"]

    # markera busy direkt
    drone["status"] = "busy"
    r.set(f"drone:{drone_id}", json.dumps(drone))

    print("Starting mission for drone:", drone_id)

    threading.Thread(
        target=fly_to,
        args=(drone_id, from_coords, to_coords, r)
    ).start()
