from flask import Flask, request, render_template, redirect, url_for
from controller import send_mission
import redis
import json

app = Flask(__name__)

# ================================
# Redis (databasen från era drönare)
# ================================
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# ================================
# Farmers (login + coords)
# ================================
FARMERS = {
    "anna": {"password": "pass123", "from": (55.81904, 13.42416), "to": (55.82013, 13.42103)},
    "erik": {"password": "erikpwd", "from": (55.81904, 13.42416), "to": (13.2200, 55.7200)},
    "lisa": {"password": "lisapwd", "from": (55.81904, 13.42416), "to": (13.2300, 55.7300)}
}

# ================================
# 🔐 LOGIN
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
# 📦 ORDER-SIDA
# ================================
@app.route('/order/<farmer>')
def order_page(farmer):
    return render_template('order.html', farmer=farmer)


# ================================
# 🚁 SKICKA DRÖNARE
# ================================
@app.route('/send_order/<farmer>', methods=['POST'])
def send_order(farmer):

    coords = FARMERS[farmer]

    send_mission(coords["from"], coords["to"])

    # Gå till karta efter klick
    return redirect(url_for('map_page'))


# ================================
# 🗺️ KARTA (index.html)
# ================================
@app.route('/map')
def map_page():
    return render_template('index.html')


# ================================
# 🔥 VIKTIG: skicka drönare till frontend
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
