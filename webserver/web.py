from flask import Flask, request, render_template, redirect, url_for, jsonify, session
import redis
import json
import threading
from controller import send_mission

app = Flask(__name__)
app.secret_key = "supersecretkey"   # behövs för admin-login

r = redis.Redis(host='192.168.0.2', port=6379, decode_responses=True)

# ========================
# USERS
# ========================
USERS = {
    "anna": "pass123",
    "erik": "erikpwd",
    "lisa": "lisapwd"
}

# ========================
# ADMIN USER
# ========================
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# ========================
# ROUTES
# ========================
ROUTES = {
    "anna": {"from": (13.42416, 55.81904), "to": (13.4156, 55.8251)},
    "erik": {"from": (13.42416, 55.81904), "to": (13.4234, 55.8216)},
    "lisa": {"from": (13.42416, 55.81904), "to": (13.4200, 55.8156)}
}

# ========================
# LOGIN
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
# ADMIN LOGIN
# ========================
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')

        if user == ADMIN_USER and pw == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin'))

    return render_template('admin_login.html')


# ========================
# ORDER PAGE
# ========================
@app.route('/order/<farmer>')
def order_page(farmer):
    return render_template('order.html', farmer=farmer)


# ========================
# SEND ORDER
# ========================
@app.route('/send_order/<farmer>', methods=['POST'])
def send_order(farmer):

    route = ROUTES[farmer]
    send_mission(route["from"], route["to"])

    return redirect(url_for('map_page'))


# ========================
# MAP
# ========================
@app.route('/map')
def map_page():
    return render_template('index.html')


# ========================
# ADMIN PAGE (protected)
# ========================
@app.route('/admin')
def admin():

    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    drones = {}

    for key in r.keys("drone:*"):
        data = r.get(key)
        if data:
            drones[key] = json.loads(data)

    return render_template('admin.html', drones=drones)


# ========================
# ADMIN SEND MISSION
# ========================
@app.route('/admin/send_mission', methods=['POST'])
def admin_send_mission():

    data = request.json
    lat = data["lat"]
    lng = data["lng"]

    # Hitta första lediga drönare
    drone = None
    for key in r.keys("drone:*"):
        d = json.loads(r.get(key))
        if d["status"] == "idle":
            drone = d
            break

    if not drone:
        return "No drone available", 400

    # Skicka uppdrag till drönaren
    try:
        import requests
        requests.post(
            f"http://{drone['ip']}:5000/move",
            json={"from": [drone["longitude"], drone["latitude"]],
                  "to": [lng, lat]},
            timeout=5
        )
    except:
        return "Failed", 500

    return "OK"


# ========================
# API DRONES
# ========================
@app.route('/get_drones')
def get_drones():

    drones = {}

    for key in r.keys("drone:*"):
        data = r.get(key)
        if data:
            d = json.loads(data)
            drones[d["id"]] = d

    return jsonify(drones)


# ========================
# START
# ========================
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
