from flask import Flask, request
from flask_cors import CORS
import subprocess
import requests
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)

# ================================
# Unique ID for this drone
# ================================
myID = "1"   # På andra Raspberry Pi: ändra till "2"

# ================================
# Database server address (Server Pi)
# ================================
SERVER = "http://192.168.0.11:5001/drone"   # ÄNDRA till er server-IP

# ================================
# Get initial position
# ================================
if os.path.exists("current_location.txt"):
    with open("current_location.txt", "r") as f:
        line = f.readline().strip()
        current_longitude, current_latitude = line.split(",")
else:
    # Default startposition (OSM coords)
    current_longitude = "13.2005"
    current_latitude = "55.7059"
    with open("current_location.txt", "w") as f:
        f.write(f"{current_longitude},{current_latitude}")

# ================================
# Send initial position to database server
# ================================
drone_info = {
    'id': myID,
    'longitude': current_longitude,
    'latitude': current_latitude,
    'status': 'idle'
}

requests.post(SERVER, json=drone_info)


# ================================
# Receive delivery request
# ================================
@app.route('/', methods=['POST'])
def main():

    coords = request.json

    # Read current position from file
    with open("current_location.txt", "r") as f:
        line = f.readline().strip()
        current_longitude, current_latitude = line.split(",")

    from_coord = coords['from']
    to_coord = coords['to']

    # Update status to busy
    drone_info = {
        'id': myID,
        'longitude': current_longitude,
        'latitude': current_latitude,
        'status': 'busy'
    }

    requests.post(SERVER, json=drone_info)

    # Start simulator as background process
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
