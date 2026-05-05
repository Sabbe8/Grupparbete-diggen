import time
import json

def fly_to(drone_id, from_coord, to_coord, r, ip):

    lat = from_coord[1]
    lon = from_coord[0]

    target_lat = to_coord[1]
    target_lon = to_coord[0]

    steps = 100
    lat_step = (target_lat - lat) / steps
    lon_step = (target_lon - lon) / steps

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

        time.sleep(0.2)

    r.set(f"drone:{drone_id}", json.dumps({
        "id": drone_id,
        "latitude": lat,
        "longitude": lon,
        "status": "idle",
        "ip": ip
    }))
