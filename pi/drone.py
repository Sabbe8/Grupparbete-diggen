from flask import Flask, request
import redis
import json
import threading
from simulator import fly_to

app = Flask(__name__)

# ⚠️ VIKTIGT: denna måste peka på SAMMA Redis som webben använder
r = redis.Redis(
    host="192.168.0.2",  # ← din dator (webserver + Redis)
    port=6379,
    decode_responses=True
)

DRONE_ID = "1"

# startposition
lat = 55.81904
lon = 13.42416
ip = "192.168.0.10"  # ← Johns Raspberry Pi IP


# =========================
# REGISTER DRONE
# =========================
def register(status="idle"):
    r.set(f"drone:{DRONE_ID}", json.dumps({
        "id": DRONE_ID,
        "latitude": lat,
        "longitude": lon,
        "status": status,
        "ip": ip
    }))


# 🔥 register direkt vid start (VIKTIGT efter FLUSHALL)
register("idle")


# =========================
# RECEIVE MISSION
# =========================
@app.route('/move', methods=['POST'])
def move():

    data = request.json

    from_coord = data["from"]
    to_coord = data["to"]

    # markera busy i Redis
    register("busy")

    # starta flygning i bakgrund
    threading.Thread(
        target=fly_to,
        args=(DRONE_ID, from_coord, to_coord, r)
    ).start()

    return "OK"


# =========================
# HEALTH CHECK (valfri men bra)
# =========================
@app.route('/ping')
def ping():
    return "drone alive"


# =========================
# START SERVER
# =========================
if __name__ == '__main__':
    print("Drone starting on Raspberry Pi...")
    register("idle")
    app.run(host="0.0.0.0", port=5000)
