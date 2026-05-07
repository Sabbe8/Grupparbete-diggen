import redis
import json
import time
import random

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


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



while True:

    for i, d in drones.items():


        d["latitude"] += random.uniform(-d["speed"], d["speed"])
        d["longitude"] += random.uniform(-d["speed"], d["speed"])

    
        if random.random() < 0.01:
            d["status"] = "busy"
        else:
            d["status"] = "idle"


        r.set(f"drone:{i}", json.dumps(d))

    time.sleep(1)
