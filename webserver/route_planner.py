from flask import Flask, request
import redis
import json
import requests

app = Flask(__name__)
r = redis.Redis(host='192.168.0.2', port=6379, decode_responses=True)

def get_available_drone():
    for key in r.keys("drone:*"):
        drone = json.loads(r.get(key))
        if drone["status"] == "idle":
            return drone
    return None

@app.route('/request_drone', methods=['POST'])
def request_drone():
    data = request.json
    from_coords = data['from']
    to_coords = data['to']

    drone = get_available_drone()
    if not drone:
        return "No available drone"

    ip = drone["ip"]
    url = f"http://{ip}:5000/move"

    try:
        requests.post(url, json={"from": from_coords, "to": to_coords})
    except Exception as e:
        print("Error:", e)
        return "Failed to send request"

    return "Mission sent"

if __name__ == '__main__':
    app.run(port=5002)
