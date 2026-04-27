from flask import Flask, request, render_template, redirect, url_for
import redis
import json
import threading
from controller import send_mission

app = Flask(__name__)

# ================================
# Redis
# ================================
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# ================================
# Users
# ================================
FARMERS = {
    "anna": {"password": "pass123", "from": (13.42416, 55.81904), "to": (13.4156, 55.8251)},
    "erik": {"password": "erikpwd", "from": (13.42416, 55.81904), "to": (13.4234, 55.8216)},
    "lisa": {"password": "lisapwd", "from": (13.42416, 55.81904), "to": (13.4200, 55.8156)}
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
# SEND ORDER
# ================================
@app.route('/send_order/<farmer>', methods=['POST'])
def send_order(farmer):

    coords = FARMERS[farmer]

    print("WEB ORDER")
    print("FROM:", coords["from"])
    print("TO:", coords["to"])

    threading.Thread(
        target=send_mission,
        args=(coords["from"], coords["to"])
    ).start()

    return redirect(url_for('map_page'))


# ================================
# MAP (index.html)
# ================================
@app.route('/map')
def map_page():
    return render_template('index.html')


# ================================
# GET DRONES (för kartan)
# ================================
@app.route('/get_drones')
def get_drones():

    drones = {}

    for key in r.keys("drone:*"):
        data = json.loads(r.get(key))
        drones[data['id']] = data

    return drones


# ================================
# START SERVER
# ================================
if __name__ == '__main__':
    app.run(port=5000, debug=True)
