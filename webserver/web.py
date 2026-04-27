from flask import Flask, request, render_template, redirect, url_for
import redis
import json
import threading
from controller import send_mission

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# ================================
# USERS
# ================================
USERS = {
    "anna": "pass123",
    "erik": "erikpwd",
    "lisa": "lisapwd"
}

# ================================
# LOGIN
# ================================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')

        if user in USERS and USERS[user] == pw:
            return redirect(url_for('order_page', farmer=user))

    return render_template('login.html')


# ================================
# ORDER PAGE
# ================================
@app.route('/order/<farmer>')
def order_page(farmer):
    return render_template('order.html', farmer=farmer)


# ================================
# SEND ORDER (USER)
# ================================
@app.route('/send_order/<farmer>', methods=['POST'])
def send_order(farmer):

    from_coord = (
        float(request.form["from_long"]),
        float(request.form["from_lat"])
    )

    to_coord = (
        float(request.form["to_long"]),
        float(request.form["to_lat"])
    )

    print("USER ORDER:", farmer, from_coord, to_coord)

    threading.Thread(
        target=send_mission,
        args=(from_coord, to_coord)
    ).start()

    return redirect(url_for('map_page'))


# ================================
# MAP PAGE
# ================================
@app.route('/map')
def map_page():
    return render_template('index.html')


# ================================
# ADMIN PAGE
# ================================
@app.route('/admin')
def admin():

    drones = {}

    for key in r.keys("drone:*"):
        drones[key] = json.loads(r.get(key))

    return render_template('admin.html', drones=drones)


# ================================
# ADMIN SEND MISSION
# ================================
@app.route('/admin/send', methods=['POST'])
def admin_send():

    drone_id = request.form["drone_id"]

    drone = json.loads(r.get(f"drone:{drone_id}"))
    ip = drone["ip"]

    url = f"http://{ip}:5000/"

    requests.post(url, json={
        "from": (
            float(request.form["from_long"]),
            float(request.form["from_lat"])
        ),
        "to": (
            float(request.form["to_long"]),
            float(request.form["to_lat"])
        )
    })

    return redirect(url_for('admin'))


# ================================
# API FOR MAP
# ================================
@app.route('/get_drones')
def get_drones():
    drones = {}

    for key in r.keys("drone:*"):
        drones[key] = json.loads(r.get(key))

    return drones


if __name__ == '__main__':
    app.run(port=5000, debug=True)
