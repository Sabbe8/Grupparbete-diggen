import math
import requests
import argparse
import time

def getMovement(src, dst):
    speed = 0.0001
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


def run(id, current_coords, from_coords, to_coords, SERVER_URL):

    drone_coords = current_coords

    # ================================
    # Move to pickup location
    # ================================
    while math.dist(drone_coords, from_coords) > 0.0001:

        d_long, d_la = getMovement(drone_coords, from_coords)

        drone_coords = moveDrone(drone_coords, d_long, d_la)

        drone_info = {
            'id': id,
            'longitude': drone_coords[0],
            'latitude': drone_coords[1],
            'status': 'busy'
        }

        requests.post(SERVER_URL, json=drone_info)
        time.sleep(0.1)

    # ================================
    # Move to delivery location
    # ================================
    while math.dist(drone_coords, to_coords) > 0.0001:

        d_long, d_la = getMovement(drone_coords, to_coords)

        drone_coords = moveDrone(drone_coords, d_long, d_la)

        drone_info = {
            'id': id,
            'longitude': drone_coords[0],
            'latitude': drone_coords[1],
            'status': 'busy'
        }

        requests.post(SERVER_URL, json=drone_info)
        time.sleep(0.1)

    # ================================
    # Delivery completed → set idle
    # ================================
    drone_info = {
        'id': id,
        'longitude': drone_coords[0],
        'latitude': drone_coords[1],
        'status': 'idle'
    }

    requests.post(SERVER_URL, json=drone_info)

    return drone_coords[0], drone_coords[1]


if __name__ == "__main__":

    # ================================
    # Database server address
    # ================================
    SERVER_URL = "http://192.168.0.11:5001/drone"   # ÄNDRA till er server-IP

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

    # ================================
    # Save final position to file
    # ================================
    with open("current_location.txt", "w") as f:
        f.write(f"{drone_long},{drone_lat}")