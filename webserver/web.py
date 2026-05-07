from flask import Flask, request, render_template, redirect, url_for, jsonify, session
import redis
import json
import threading
from controller import send_mission

app = Flask(__name__)
app.secret_key = "supersecretkey"   

r = redis.Redis(host='192.168.0.2', port=6379, decode_responses=True)


USERS = {
    "anna": "pass123",
    "erik": "erikpwd",
    "lisa": "lisapwd"
}


ADMIN_USER = "admin"
ADMIN_PASS = "1234"




STATION = (13.42416, 55.81904)  # lon, lat

ROUTES = {
    "anna": {
        "from": STATION,
        "area": [
            (13.412180, 55.823721),
            (13.418359, 55.824540),
            (13.416347, 55.826065),
            (13.411557, 55.824957)
        ],
        "problem": (13.4234, 55.8191)
    },

    "erik": {
        "from": STATION,
        "area": [
            (13.427109, 55.816642),
            (13.428230, 55.813072),
            (13.421857, 55.812509),
            (13.419390, 55.815510)
            
        ],
        "problem": (13.4276, 55.8212)
    },

    "lisa": {
        "from": STATION,
        "area": [
            (13.427457, 55.819655),
            (13.437815, 55.822099),
            (13.436283, 55.823717),
            (13.4245415, 55.823476)
        ],
        "problem": (13.4202, 55.8171)
    }
}


@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')

        if user in USERS and USERS[user] == pw:
            session["farmer"] = user
            return redirect(url_for('order_page', farmer=user))

    return render_template('login.html')



@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')

        if user == ADMIN_USER and pw == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin'))

    return render_template('admin_login.html')



@app.route('/order/<farmer>')
def order_page(farmer):
    return render_template('order.html', farmer=farmer)


@app.route('/send_order/<farmer>', methods=['POST'])
def send_order(farmer):

    route = ROUTES[farmer]

    send_mission(
    route["from"],
    route["area"],
    route["problem"],
    owner=farmer
    )

    return redirect(url_for('map_page'))


@app.route('/map')
def map_page():
    return render_template('index.html')


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



@app.route('/admin/send_mission', methods=['POST'])
def admin_send_mission():

    data = request.json
    lat = data["lat"]
    lng = data["lng"]

    # Skapa ett litet fyrkantigt fält runt klicket
    size_lon = 0.0015
    size_lat = 0.0010

    area = [
        (lng - size_lon, lat - size_lat),
        (lng + size_lon, lat - size_lat),
        (lng + size_lon, lat + size_lat),
        (lng - size_lon, lat + size_lat)
    ]

    problem = (lng, lat)

    send_mission(
        STATION,
        area,
        problem
    )

    return "OK"



@app.route('/get_drones')
def get_drones():

    drones = {}

    current_user = session.get("farmer")
    is_admin = session.get("admin")

    for key in r.keys("drone:*"):
        data = r.get(key)

        if data:
            d = json.loads(data)

            # Admin ser alla drönare
            if is_admin:
                drones[d["id"]] = d

            # Vanlig användare ser bara sin egen aktiva drönare
            else:
                if d.get("owner") == current_user:
                    drones[d["id"]] = d

    return jsonify(drones)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
