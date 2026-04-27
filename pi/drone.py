from flask import Flask, request
from flask_cors import CORS
import subprocess
import requests
import os
import socket

app = Flask(__name__)
CORS(app, supports_credentials=True)

# ================================
# Drone ID (ändra per Pi)
# ================================
myID = "1"

# ================================
# Database server (DIN DATOR)
# ================================
SERVER = "http://192.168.0.2:5001/drone"


# ================================
# Hämta Raspberry Pi IP
# ================================
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


# ================================
# Start position
# ================================
if os.path.exists("current_location.txt"):
    with open("current_location.txt", "r") as f:
        line = f.readline().strip()
        current_longitude, current_latitude = line.split(",")
        current_longitude = float(current_longitude)
        current_latitude = float(current_latitude)
else:
    current_longitude = 13.2005
    current_latitude = 55.7059

    with open("current_location.txt", "w") as f:
        f.write(f"{current_longitude},{current_latitude}")


# ================================
# Registrera drone i server
# ================================
def register(status="idle"):
    try:
        requests.post(SERVER, json={
            "id": myID,
            "ip": myIP,
            "longitude": current_longitude,
            "latitude": current_latitude,
            "status": status
        }, timeout=3)
    except Exception as e:
        print("Server not reachable:", e)


register("idle")

print("Drone started:", myID, "IP:", myIP)


# ================================
# Ta emot uppdrag
# ================================
@app.route('/', methods=['POST'])
def main():

    coords = request.json

    from_coord = coords['from']
    to_coord = coords['to']

    # uppdatera status
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

    return "New route received"


# ================================
# START SERVER
# ================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
