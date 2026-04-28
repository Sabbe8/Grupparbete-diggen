from flask import Flask, request, render_template, redirect, url_for
import redis
import json
import threading
from controller import send_mission

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# ========================
# USERS
# ========================
USERS = {
    "anna": "pass123",
    "erik": "erikpwd",
    "lisa": "lisapwd"
}

# ========================
# FASTA RUTTER
# ========================
ROUTES = {
    "anna": {
        "from": (13.42416, 55.81904),
        "to": (13.4156, 55.8251)
    },
    "erik": {
        "from": (13.42416, 55.81904),
        "to": (13.4234, 55.8216)
    },
    "lisa": {
        "from": (13.42416, 55.81904),
        "to": (13.4200, 55.8156)
    }
}

# ========================
# LOGIN (BONDE)
# ========================
@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')

        if user in USERS and USERS[user] == pw:
            return redirect(url_for('order_page', farmer=user))

    return render_template('login.html')


# ========================
# ORDER PAGE
# ========================
@app.route('/order/<farmer>')
def order_page(farmer):
    return render_template('order.html', farmer=farmer)


# ========================
# SEND DRONE (FAST RUTT)
# ========================
@app.route('/send_order/<farmer>', methods=['POST'])
def send_order(farmer):

    route = ROUTES[farmer]

    from_coord = route["from"]
    to_coord = route["to"]

    threading.Thread(
        target=send_mission,
        args=(from_coord, to_coord)
    ).start()

    return redirect(url_for('map_page'))


# ========================
# MAP
# ========================
@app.route('/map')
def map_page():
    return render_template('index.html')


# ========================
# ADMIN LOGIN
# ========================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "admin" and password == "admin123":
            return redirect(url_for('admin'))

    return render_template('admin_login.html')


# ========================
# ADMIN DASHBOARD
# ========================
@app.route('/admin')
def admin():

    drones = {}

    for key in r.keys("drone:*"):
        data = r.get(key)
        if data:
            drones[key] = json.loads(data)

    return render_template('admin.html', drones=drones)


# ========================
# ADMIN CLICK ON MAP → MISSION
# ========================
@app.route('/admin/send_mission', methods=['POST'])
def admin_send_mission():

    data = request.json

    lat = data["lat"]
    lng = data["lng"]

    # hitta ledig drone
    drone = None

    for key in r.keys("drone:*"):
        d = json.loads(r.get(key))
        if d["status"] == "idle":
            drone = d
            break

    if not drone:
        return {"status": "no drone available"}

    from_coord = (drone["longitude"], drone["latitude"])
    to_coord = (lng, lat)

    threading.Thread(
        target=send_mission,
        args=(from_coord, to_coord)
    ).start()

    return {"status": "sent"}


# ========================
# API: DRONES
# ========================
@app.route('/get_drones')
def get_drones():

    drones = {}

    for key in r.keys("drone:*"):
        data = r.get(key)
        if data:
            drone = json.loads(data)

            drones[drone["id"]] = {
                "latitude": drone["latitude"],
                "longitude": drone["longitude"],
                "status": drone["status"],
                "ip": drone.get("ip")
            }

    return drones


# ========================
# START
# ========================
if __name__ == '__main__':
    app.run(port=5000, debug=True)
