from flask import Flask, request
import requests
import subprocess
import socket
import os
import json

app = Flask(__name__)

myID = "1"
SERVER = "http://192.168.0.2:5001/drone"


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "127.0.0.1"
    finally:
        s.close()


myIP = get_ip()


# start position
if os.path.exists("current_location.txt"):
    with open("current_location.txt") as f:
        lon, lat = f.read().split(",")
        current_longitude = float(lon)
        current_latitude = float(lat)
else:
    current_longitude = 13.2
    current_latitude = 55.7


def register(status):
    try:
        requests.post(SERVER, json={
            "id": myID,
            "ip": myIP,
            "longitude": current_longitude,
            "latitude": current_latitude,
            "status": status
        })
    except:
        pass


register("idle")


@app.route('/', methods=['POST'])
def receive():

    global current_longitude, current_latitude

    data = request.json

    from_coord = data["from"]
    to_coord = data["to"]

    print("DRONE GOT:", from_coord, to_coord)

    register("busy")

    subprocess.Popen([
        "python3", "simulator.py",
        "--clong", str(current_longitude),
        "--clat", str(current_latitude),
        "--tlong", str(to_coord[0]),
        "--tlat", str(to_coord[1]),
        "--id", myID
    ])

    current_longitude = to_coord[0]
    current_latitude = to_coord[1]

    with open("current_location.txt", "w") as f:
        f.write(f"{current_longitude},{current_latitude}")

    register("idle")

    return "OK"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
