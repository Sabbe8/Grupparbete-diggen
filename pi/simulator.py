import time
import json


def save_drone(drone_id, lat, lon, status, r, ip, owner=None):
    r.set(f"drone:{drone_id}", json.dumps({
        "id": drone_id,
        "latitude": lat,
        "longitude": lon,
        "status": status,
        "ip": ip,
        "owner": owner
    }))


def distance(p1, p2):

    lon1, lat1 = p1
    lon2, lat2 = p2

    return ((lon2 - lon1) ** 2 + (lat2 - lat1) ** 2) ** 0.5


def order_area_from_nearest_corner(start, area):
    nearest_index = min(
        range(len(area)),
        key=lambda i: distance(start, area[i])
    )


    ordered = area[nearest_index:] + area[:nearest_index]


    ordered.append(ordered[0])

    return ordered


def move_smooth(drone_id, start_lon, start_lat, target_lon, target_lat, r, ip, owner=None):


    steps = 300
    sleep_time = 0.03

    for i in range(steps + 1):
        t = i / steps

        smooth_t = t * t * (3 - 2 * t)

        lon = start_lon + (target_lon - start_lon) * smooth_t
        lat = start_lat + (target_lat - start_lat) * smooth_t
        save_drone(drone_id, lat, lon, "busy", r, ip, owner)

        time.sleep(sleep_time)


def fly_to(drone_id, from_coord, area, problem, r, ip, owner=None):


    current_lon = from_coord[0]
    current_lat = from_coord[1]

    route = order_area_from_nearest_corner(from_coord, area)


    for point in route:
        target_lon = point[0]
        target_lat = point[1]

        move_smooth(
            drone_id,
            current_lon,
            current_lat,
            target_lon,
            target_lat,
            r,
            ip,
            owner
        )

        current_lon = target_lon
        current_lat = target_lat


    station_lon = from_coord[0]
    station_lat = from_coord[1]

    move_smooth(
        drone_id,
        current_lon,
        current_lat,
        station_lon,
        station_lat,
        r,
        ip,
        owner
    )

    # Klar, tillbaka vid stationen
    save_drone(drone_id, station_lat, station_lon, "idle", r, ip, None)
