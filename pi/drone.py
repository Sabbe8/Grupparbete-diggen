import subprocess
import requests
import os

# ================================
# Drone ID
# ================================
myID = "1"

# ================================
# Database server
# ================================
SERVER = "http://localhost:5001/drone"

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
    "id": myID,
    "longitude": current_longitude,
    "latitude": current_latitude,
    "status": "idle"
})

print("Drone started:", myID)

# ================================
# Väntar på uppdrag (via route_planner)
# ================================
# OBS: drone.py gör inget aktivt själv längre
