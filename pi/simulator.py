import time
import json


def save_drone(drone_id, lat, lon, status, r, ip):
    """
    Sparar drönarens position/status i Redis.
    Webbsidan läser detta via /get_drones.
    """
    r.set(f"drone:{drone_id}", json.dumps({
        "id": drone_id,
        "latitude": lat,
        "longitude": lon,
        "status": status,
        "ip": ip
    }))


def distance(p1, p2):
    """
    Räknar enkel distans mellan två koordinater.
    p = (longitude, latitude)
    """
    lon1, lat1 = p1
    lon2, lat2 = p2

    return ((lon2 - lon1) ** 2 + (lat2 - lat1) ** 2) ** 0.5


def order_area_from_nearest_corner(start, area):
    """
    Tar ett fält med fyra hörn.
    Väljer det hörn som är närmast stationen/starten.
    Sedan gör den en rutt runt hela fältet.
    """

    # Hitta vilket hörn som är närmast startpunkten
    nearest_index = min(
        range(len(area)),
        key=lambda i: distance(start, area[i])
    )

    # Rotera listan så närmaste hörn kommer först
    ordered = area[nearest_index:] + area[:nearest_index]

    # Lägg till första hörnet igen så fyrkanten stängs
    ordered.append(ordered[0])

    return ordered


def move_smooth(drone_id, start_lon, start_lat, target_lon, target_lat, r, ip):
    """
    Flyttar drönaren mjukt mellan två punkter.
    """

    steps = 300
    sleep_time = 0.03

    for i in range(steps + 1):
        t = i / steps

        # Smoothstep = mjuk start och mjukt stopp
        smooth_t = t * t * (3 - 2 * t)

        lon = start_lon + (target_lon - start_lon) * smooth_t
        lat = start_lat + (target_lat - start_lat) * smooth_t

        save_drone(drone_id, lat, lon, "busy", r, ip)

        time.sleep(sleep_time)


def fly_to(drone_id, from_coord, area, problem, r, ip):
    """
    Huvudfunktionen för drönarens flygning.

    from_coord = station/startpunkt
    area = användarens fält, fyra hörn
    problem = röd punkt/skada, används senare i webben

    Alla koordinater är:
    (longitude, latitude)
    """

    # Startposition/station
    current_lon = from_coord[0]
    current_lat = from_coord[1]

    # Skapa rutt:
    # station -> närmaste hörn -> runt fältet -> tillbaka till station
    route = order_area_from_nearest_corner(from_coord, area)

    # Flyg runt fältet
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
            ip
        )

        current_lon = target_lon
        current_lat = target_lat

    # Flyg tillbaka till stationen
    station_lon = from_coord[0]
    station_lat = from_coord[1]

    move_smooth(
        drone_id,
        current_lon,
        current_lat,
        station_lon,
        station_lat,
        r,
        ip
    )

    # Klar, tillbaka vid stationen
    save_drone(drone_id, station_lat, station_lon, "idle", r, ip)
