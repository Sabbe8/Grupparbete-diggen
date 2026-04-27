from flask import Flask, request, render_template, redirect, url_for
import redis
import json
import threading
from controller import send_mission

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# ================================
# USERS (bara login här nu)
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
# SEND ORDER
# ================================
@app.route('/send_order/<farmer>', methods=['POST'])
def send_order(farmer):

    # 🔥 ta coords från HTML
    from_coord = (
        float(request.form["from_long"]),
        float(request.form["from_lat"])
    )

    to_coord = (
        float(request.form["to_long"]),
        float(request.form["to_lat"])
    )

    print("WEB SEND ORDER")
    print("USER:", farmer)
    print("FROM:", from_coord)
    print("TO:", to_coord)

    # kör mission i bakgrund
    threading.Thread(
        target=send_mission,
        args=(from_coord, to_coord)
    ).start()

    # 🔥 VIKTIG FIX: gå till kartan
    return redirect(url_for('map_page'))


# ================================
# MAP (index.html)
# ================================
@app.route('/map')
def map_page():
    return render_template('index.html')


# ================================
# DRONES (för karta)
# ================================
@app.route('/get_drones')
def get_drones():

    drones = {}

    for key in r.keys("drone:*"):
        data = json.loads(r.get(key))
        drones[data['id']] = data

    return drones


# ================================
# START
# ================================
if __name__ == '__main__':
    app.run(port=5000, debug=True)
