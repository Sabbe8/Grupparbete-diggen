import time
import json

def fly_to(drone_id, from_coord, to_coord, r, ip):

    # Startposition
    lat = from_coord[1]
    lon = from_coord[0]

    # Målposition
    target_lat = to_coord[1]
    target_lon = to_coord[0]

    # Fler steg = mjukare rörelse
    steps = 300

    # Beräkna små steg
    lat_step = (target_lat - lat) / steps
    lon_step = (target_lon - lon) / steps

    # Flyg i små, mjuka steg
    for _ in range(steps):
        lat += lat_step
        lon += lon_step

        # Uppdatera Redis med ny position
        r.set(f"drone:{drone_id}", json.dumps({
            "id": drone_id,
            "latitude": lat,
            "longitude": lon,
            "status": "busy",
            "ip": ip
        }))

        # Kortare sleep = mjukare animation
        time.sleep(0.1)

    # När drönaren är framme
    r.set(f"drone:{drone_id}", json.dumps({
        "id": drone_id,
        "latitude": lat,
        "longitude": lon,
        "status": "idle",
        "ip": ip
    }))
