import redis
import json
import time
import random

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# =========================
# SKAPA DRÖNARE
# =========================
drones = {}

NUM_DRONES = 5  # ändra till 2–10

for i in range(1, NUM_DRONES + 1):

    drones[i] = {
        "id": str(i),
        "latitude": 55.8190 + random.uniform(-0.01, 0.01),
        "longitude": 13.4240 + random.uniform(-0.01, 0.01),
        "status": "idle",
        "speed": random.uniform(0.00005, 0.00015)
    }


# =========================
# LOOP (SIMULERING)
# =========================
while True:

    for i, d in drones.items():

        # 🟢 slumpmässig rörelse
        d["latitude"] += random.uniform(-d["speed"], d["speed"])
        d["longitude"] += random.uniform(-d["speed"], d["speed"])

        # 🔴 ibland "busy"
        if random.random() < 0.01:
            d["status"] = "busy"
        else:
            d["status"] = "idle"

        # 🧠 skriv till Redis
        r.set(f"drone:{i}", json.dumps(d))

    time.sleep(1)
