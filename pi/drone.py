from flask import Flask, request
from flask_cors import CORS
import subprocess
import requests
import os
import socket

app = Flask(__name__)
CORS(app)

myID = "1"
SERVER = "http://192.168.0.2:5001/drone"


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


myIP = get_ip()


if os.path.exists("current_location.txt"):
    with open("current_location.txt", "r") as f:
        lon, lat = f.readline().split(",")
        current_longitude = float(lon)
        current_latitude = float(lat)
else:
    current_longitude = 13.2005
    current_latitude = 55.7059


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
        print("SERVER ERROR")


register("idle")

print("DRONE STARTED:", myID, myIP)


@app.route('/', methods=['POST'])
def main():

    global current_longitude, current_latitude

    coords = request.json

    from_coord = coords["from"]
    to_coord = coords["to"]

    print("DRONE RECEIVED")
    print("FROM:", from_coord)
    print("TO:", to_coord)

    register("busy")

    subprocess.Popen([
        "python3", "simulator.py",
        "--clong", str(current_longitude),
        "--clat", str(current_latitude),
        "--flong", str(from_coord[0]),
        "--flat", str(from_coord[1]),
        "--tlong", str(to_coord[0]),
        "--tlat", str(to_coord[1]),
        "--id", myID
    ])

    # uppdatera position
    current_longitude = to_coord[0]
    current_latitude = to_coord[1]

    with open("current_location.txt", "w") as f:
        f.write(f"{current_longitude},{current_latitude}")

    register("idle")

    return "OK"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
