from flask import Flask, request, render_template, redirect, url_for
import redis
import json
import threading
from controller import send_mission

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

FARMERS = {
    "anna": {"password": "pass123", "from": (13.42416, 55.81904), "to": (13.4156, 55.8251)},
    "erik": {"password": "erikpwd", "from": (13.42416, 55.81904), "to": (13.4234, 55.8216)},
    "lisa": {"password": "lisapwd", "from": (13.42416, 55.81904), "to": (13.4200, 55.8156)}
}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')

        if user in FARMERS and FARMERS[user]["password"] == pw:
            return redirect(url_for('order_page', farmer=user))

    return render_template('login.html')


@app.route('/order/<farmer>')
def order_page(farmer):
    return render_template('order.html', farmer=farmer)


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

    return redirect(url_for('login'))


@app.route('/get_drones')
def get_drones():
    drones = {}

    for key in r.keys("drone:*"):
        data = json.loads(r.get(key))
        drones[data['id']] = data

    return drones


if __name__ == '__main__':
    app.run(port=5000, debug=True)
