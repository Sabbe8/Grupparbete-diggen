from flask import Flask, request, render_template, redirect, url_for
from controller import send_mission
import redis
import json
import threading   # 🔥 NY

app = Flask(__name__)

# ================================
# Redis
# ================================
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# ================================
# Farmers
# ================================
FARMERS = {
    "anna": {"password": "pass123", "from": (13.42416, 55.81904), "to": (13.4114, 55.8252)},
    "erik": {"password": "erikpwd", "from": (13.42416, 55.81904), "to": (13.4200, 55.8300)},
    "lisa": {"password": "lisapwd", "from": (13.42416, 55.81904), "to": (13.4300, 55.8100)}
}

# ================================
# LOGIN
# ================================
@app.route('/', methods=['GET', 'POST'])
def login():
    message = ""

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in FARMERS and FARMERS[username]['password'] == password:
            return redirect(url_for('order_page', farmer=username))
        else:
            message = "Fel namn eller lösenord!"

    return render_template('login.html', message=message)


# ================================
# ORDER PAGE
# ================================
@app.route('/order/<farmer>')
def order_page(farmer):
    return render_template('order.html', farmer=farmer)


# ================================
# SEND ORDER (FIXAD)
# ================================
@app.route('/send_order/<farmer>', methods=['POST'])
def send_order(farmer):

    coords = FARMERS[farmer]

    print("FARMER:", farmer)
    print("FROM:", coords["from"])
    print("TO:", coords["to"])

    # 🔥 Kör i bakgrunden (snabb redirect)
    threading.Thread(
        target=send_mission,
        args=(coords["from"], coords["to"])
    ).start()

    return redirect(url_for('map_page'))


# ================================
# MAP
# ================================
@app.route('/map')
def map_page():
    return render_template('index.html')


# ================================
# GET DRONES
# ================================
@app.route('/get_drones')
def get_drones():

    drones = {}

    for key in r.keys("drone:*"):
        data = json.loads(r.get(key))

        drones[data['id']] = {
            "longitude": float(data['longitude']),
            "latitude": float(data['latitude']),
            "status": data['status']
        }

    return drones


# ================================
# START
# ================================
if __name__ == '__main__':
    app.run(port=5000, debug=True)
