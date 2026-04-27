from flask import Flask, request, render_template, redirect, url_for
import redis
import json

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
# ADMIN (enkel och säker)
# ========================

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"


# ========================
# USER LOGIN
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
# MAP
# ========================
@app.route('/map')
def map_page():
    return render_template('index.html')


# ========================
# 🔥 ADMIN LOGIN (FIX)
# ========================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "admin" and password == "admin123":
            return redirect(url_for('admin'))

    return render_template('admin_login.html')


@app.route('/admin')
def admin():

    drones = {}

    for key in r.keys("drone:*"):
        drones[key] = json.loads(r.get(key))

    return render_template('admin.html', drones=drones)

# ========================
# ADMIN PAGE
# ========================
@app.route('/admin')
def admin():

    drones = {}

    for key in r.keys("drone:*"):
        drones[key] = json.loads(r.get(key))

    return render_template('admin.html', drones=drones)


# ========================
# API
# ========================
@app.route('/get_drones')
def get_drones():

    drones = {}

    for key in r.keys("drone:*"):
        drones[key] = json.loads(r.get(key))

    return drones


if __name__ == '__main__':
    app.run(port=5000, debug=True)
