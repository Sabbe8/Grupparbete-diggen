from flask import Flask, request
import redis
import json

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.route('/drone', methods=['POST'])
def update_drone():

    data = request.json

    drone_id = data['id']

    drone_info = {
        "id": drone_id,
        "longitude": data['longitude'],
        "latitude": data['latitude'],
        "status": data['status'],
        "ip": request.remote_addr   # 🔥 viktigt!
    }

    r.set(f"drone:{drone_id}", json.dumps(drone_info))

    return "OK"

if __name__ == '__main__':
    app.run(port=5001)