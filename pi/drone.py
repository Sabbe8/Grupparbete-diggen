from flask import Flask, request
import redis
import json
import threading
import traceback
from simulator import fly_to

app = Flask(__name__)

# 🟢 Redis på din dator
r = redis.Redis(
    host="192.168.0.2",
    port=6379,
    decode_responses=True
)

DRONE_ID = "1"

lat = 55.81904
lon = 13.42416

ip = "192.168.0.10"


# ========================
# REGISTER
# ========================
def register(status="idle"):
    try:
        r.set(f"drone:{DRONE_ID}", json.dumps({
            "id": DRONE_ID,
            "latitude": lat,
            "longitude": lon,
            "status": status,
            "ip": ip
        }))
    except Exception as e:
        print("Redis error:", e)


register("idle")


# ========================
# MOVE DRONE
# ========================
@app.route('/move', methods=['POST'])
def move():

    try:
        data = request.json

        from_coord = data["from"]
        to_coord = data["to"]

        register("busy")

        threading.Thread(
            target=fly_to,
            args=(DRONE_ID, from_coord, to_coord, r)
        ).start()

        return "OK"

    except Exception as e:
        print("DRONE ERROR:")
        traceback.print_exc()
        return "error", 500


# ========================
# START
# ========================
if __name__ == '__main__':
    print("Drone starting...")
    register("idle")
    app.run(host="0.0.0.0", port=5000)
