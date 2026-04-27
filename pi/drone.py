from flask import Flask, request
from flask_cors import CORS
import subprocess
import requests
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)

# ================================
# Drone ID
# ================================
myID = "1"   # ändra till "2" på andra Raspberry Pi

# ================================
# Database server (ändra IP vid behov)
# ================================
SERVER = "http://192.168.0.3:5001/drone"

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
# Skicka initial status
# ================================
requests.post(SERVER, json={
    'id': myID,
    'longitude': current_longitude,
    'latitude': current_latitude,
    'status': 'idle'
})

print("Drone started:", myID)

# ================================
# Ta emot uppdrag
# ================================
@app.route('/', methods=['POST'])
def main():

    coords = request.json

    # Läs nuvarande position
    with open("current_location.txt", "r") as f:
        line = f.readline().strip()
        current_longitude, current_latitude = line.split(",")
        current_longitude = float(current_longitude)
        current_latitude = float(current_latitude)

    from_coord = coords['from']
    to_coord = coords['to']

    # Uppdatera status
    requests.post(SERVER, json={
        'id': myID,
        'longitude': current_longitude,
        'latitude': current_latitude,
        'status': 'busy'
    })

    # Starta simulator
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
    app.run(debug=True, host='0.0.0.0', port=5000)
