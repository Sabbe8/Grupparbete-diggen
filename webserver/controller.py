import redis
import json
import requests

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
    drone_ip = drone["ip"]

    # markera busy i redis
    drone["status"] = "busy"
    r.set(f"drone:{drone_id}", json.dumps(drone))

    print("Sending mission to drone:", drone_id)

    # 👉 SKICKA TILL RASPBERRY PI
    try:
        requests.post(
            f"http://{drone_ip}:5000/move",
            json={
                "from": from_coords,
                "to": to_coords
            },
            timeout=3
        )
    except Exception as e:
        print("Drone unreachable:", e)
