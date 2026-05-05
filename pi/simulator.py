import time
import json
import math

def fly_to(drone_id, from_coord, to_coord, r, ip):

    # Startposition
    lat = from_coord[1]
    lon = from_coord[0]

    # Målposition
    target_lat = to_coord[1]
    target_lon = to_coord[0]

    # Lite snabbare men fortfarande mjukt
    steps = 200
    sleep_time = 0.08

    lat_step = (target_lat - lat) / steps
    lon_step = (target_lon - lon) / steps

    # Flyg mot målet
    for _ in range(steps):
        lat += lat_step
        lon += lon_step

        r.set(f"drone:{drone_id}", json.dumps({
            "id": drone_id,
            "latitude": lat,
            "longitude": lon,
            "status": "busy",
            "ip": ip
        }))

        time.sleep(sleep_time)

    # När drönaren är framme → flyg i en cirkel
    radius = 0.0003      # ungefär 30 meter
    circle_steps = 60    # antal punkter i cirkeln

    for i in range(circle_steps):
        angle = (i / circle_steps) * 2 * math.pi

        circle_lat = target_lat + radius * math.sin(angle)
        circle_lon = target_lon + radius * math.cos(angle)

        r.set(f"drone:{drone_id}", json.dumps({
            "id": drone_id,
            "latitude": circle_lat,
            "longitude": circle_lon,
            "status": "busy",
            "ip": ip
        }))

        time.sleep(0.08)

    # Efter cirkeln → sätt drönaren till idle
    r.set(f"drone:{drone_id}", json.dumps({
        "id": drone_id,
        "latitude": target_lat,
        "longitude": target_lon,
        "status": "idle",
        "ip": ip
    }))
