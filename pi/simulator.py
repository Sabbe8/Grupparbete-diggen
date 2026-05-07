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


def interpolate(p1, p2, t):
    lon1, lat1 = p1
    lon2, lat2 = p2

    lon = lon1 + (lon2 - lon1) * t
    lat = lat1 + (lat2 - lat1) * t

    return (lon, lat)


def create_lawnmower_path(area, rows=8):
    """
    Skapar S-format rutt över fältet.

    OBS:
    Detta funkar bäst om area har 4 hörn:
    area[0] ---- area[1]
      |            |
    area[3] ---- area[2]
    """

    # Om area råkar ha fler än 4 punkter, använd bara de första 4
    area = area[:4]

    path = []

    for i in range(rows):
        t = i / (rows - 1)

        left_point = interpolate(area[0], area[3], t)
        right_point = interpolate(area[1], area[2], t)

        # Varannan rad åt andra hållet = S-mönster
        if i % 2 == 0:
            path.append(left_point)
            path.append(right_point)
        else:
            path.append(right_point)
            path.append(left_point)

    return path


def move_smooth(drone_id, start_lon, start_lat, target_lon, target_lat, r, ip, owner=None):
    """
    Flyttar drönaren mjukt mellan två punkter.
    """

    dist = distance((start_lon, start_lat), (target_lon, target_lat))

    # Fler steg för längre sträckor
    steps = int(dist * 120000)

    # Begränsa så det inte blir för hackigt eller för långsamt
    steps = max(80, min(steps, 300))

    sleep_time = 0.03

    for i in range(steps + 1):
        t = i / steps

        # Smoothstep = mjuk start och mjukt stopp
        smooth_t = t * t * (3 - 2 * t)

        lon = start_lon + (target_lon - start_lon) * smooth_t
        lat = start_lat + (target_lat - start_lat) * smooth_t

        save_drone(drone_id, lat, lon, "busy", r, ip, owner)

        time.sleep(sleep_time)


def fly_to(drone_id, from_coord, area, problem, r, ip, owner=None):
    """
    from_coord = station/startpunkt, format: (lon, lat)
    area = fältets hörn, format: [(lon, lat), ...]
    problem = röd problem-punkt, används inte här än
    owner = anna/erik/lisa
    """

    # Start vid stationen
    current_lon = from_coord[0]
    current_lat = from_coord[1]

    # Skapa S-format rutt över fältet
    route = create_lawnmower_path(area, rows=8)

    # Flyg från stationen till första punkten i fältet
    first_point = route[0]

    move_smooth(
        drone_id,
        current_lon,
        current_lat,
        first_point[0],
        first_point[1],
        r,
        ip,
        owner
    )

    current_lon = first_point[0]
    current_lat = first_point[1]

    # Flyg igenom hela S-mönstret
    for point in route[1:]:
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
        ip,
        owner
    )

    # Klar: drönaren är idle igen och ägs inte längre av någon
    save_drone(drone_id, station_lat, station_lon, "idle", r, ip, None)