import math
import requests
import argparse
import time


def getMovement(src, dst):
    speed = 0.00005
    dst_x, dst_y = dst
    x, y = src
    direction = math.sqrt((dst_x - x)**2 + (dst_y - y)**2)

    if direction == 0:
        return 0, 0

    longitude_move = speed * ((dst_x - x) / direction)
    latitude_move = speed * ((dst_y - y) / direction)
    return longitude_move, latitude_move


def moveDrone(src, d_long, d_la):
    x, y = src
    x = x + d_long
    y = y + d_la
    return (x, y)


# =========================================
# Create circle path
# =========================================
def circleDrone(center, radius, steps):
    cx, cy = center
    positions = []

    for i in range(steps):
        angle = 2 * math.pi * i / steps
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        positions.append((x, y))

    return positions


def run(id, current_coords, from_coords, to_coords, SERVER_URL):

    start_coords = current_coords
    drone_coords = current_coords

    # =========================================
    # Flyg till farmer
    # =========================================
    while math.dist(drone_coords, from_coords) > 0.00005:

        d_long, d_la = getMovement(drone_coords, from_coords)
        drone_coords = moveDrone(drone_coords, d_long, d_la)

        requests.post(SERVER_URL, json={
            'id': id,
            'longitude': drone_coords[0],
            'latitude': drone_coords[1],
            'status': 'busy'
        })

        time.sleep(0.1)

    # =========================================
    # Flyg i cirkel
    # =========================================
    circle_points = circleDrone(from_coords, 0.0003, 40)

    for point in circle_points:

        while math.dist(drone_coords, point) > 0.00005:

            d_long, d_la = getMovement(drone_coords, point)
            drone_coords = moveDrone(drone_coords, d_long, d_la)

            requests.post(SERVER_URL, json={
                'id': id,
                'longitude': drone_coords[0],
                'latitude': drone_coords[1],
                'status': 'scanning'
            })

            time.sleep(0.1)

    # =========================================
    # Return to start
    # =========================================
    while math.dist(drone_coords, start_coords) > 0.00005:

        d_long, d_la = getMovement(drone_coords, start_coords)
        drone_coords = moveDrone(drone_coords, d_long, d_la)

        requests.post(SERVER_URL, json={
            'id': id,
            'longitude': drone_coords[0],
            'latitude': drone_coords[1],
            'status': 'returning'
        })

        time.sleep(0.1)

    # =========================================
    # Done
    # =========================================
    requests.post(SERVER_URL, json={
        'id': id,
        'longitude': drone_coords[0],
        'latitude': drone_coords[1],
        'status': 'idle'
    })

    return drone_coords[0], drone_coords[1]


if __name__ == "__main__":

    SERVER_URL = "http://192.168.0.2:5001/drone"

    parser = argparse.ArgumentParser()
    parser.add_argument("--clong", type=float)
    parser.add_argument("--clat", type=float)
    parser.add_argument("--flong", type=float)
    parser.add_argument("--flat", type=float)
    parser.add_argument("--tlong", type=float)
    parser.add_argument("--tlat", type=float)
    parser.add_argument("--id", type=str)

    args = parser.parse_args()

    current_coords = (args.clong, args.clat)
    from_coords = (args.flong, args.flat)
    to_coords = (args.tlong, args.tlat)

    drone_long, drone_lat = run(
        args.id,
        current_coords,
        from_coords,
        to_coords,
        SERVER_URL
    )

    # Save final position
    with open("current_location.txt", "w") as f:
        f.write(f"{drone_long},{drone_lat}")
