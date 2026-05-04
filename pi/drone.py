from flask import Flask, request
import redis
import json
import threading
from simulator import fly_to

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

DRONE_ID = "1"

# startposition
lat = 55.81904
lon = 13.42416


# =========================
# REGISTER DRONE
# =========================
def register(status="idle"):
    r.set(f"drone:{DRONE_ID}", json.dumps({
        "id": DRONE_ID,
        "latitude": lat,
        "longitude": lon,
        "status": status,
        "ip": "192.168.0.10"
    }))


register("idle")


# =========================
# RECEIVE MISSION
# =========================
@app.route('/', methods=['POST'])
def mission():

    data = request.json

    from_coord = data["from"]
    to_coord = data["to"]

    register("busy")

    threading.Thread(
        target=fly_to,
        args=(DRONE_ID, from_coord, to_coord, r)
    ).start()

    return "OK"


# =========================
# START SERVER
# =========================
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
