from flask import Flask, request, render_template, redirect, url_for, jsonify, session
import redis
import json
from controller import send_mission

app = Flask(__name__)
app.secret_key = "supersecretkey"

r = redis.Redis(host="192.168.0.2", port=6379, decode_responses=True)

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
            (13.412791, 55.826049),
            (13.412791, 55.824474),
            (13.412791, 55.824359),
            (13.412791, 55.825809),
            (13.412791, 55.824234),
            (13.412791, 55.824166),
            (13.412791, 55.825665),
            (13.412791, 55.825531),
            (13.412791, 55.823974),
            (13.412791, 55.823955),
            (13.412791, 55.825386),
            (13.412791, 55.825233),
            (13.412791, 55.823725),
            (13.411611, 55.825329),
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


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pw = request.form.get("password")

        if user in USERS and USERS[user] == pw:
            session.clear()
            session["farmer"] = user
            return redirect(url_for("order_page", farmer=user))

    return render_template("login.html")


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        user = request.form.get("username")
        pw = request.form.get("password")

        if user == ADMIN_USER and pw == ADMIN_PASS:
            session.clear()
            session["admin"] = True
            return redirect(url_for("admin"))

    return render_template("admin_login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/whoami")
def whoami():
    return jsonify({
        "farmer": session.get("farmer"),
        "admin": session.get("admin")
    })


@app.route("/order/<farmer>")
def order_page(farmer):
    if session.get("farmer") != farmer:
        return redirect(url_for("login"))

    return render_template("order.html", farmer=farmer)


@app.route("/send_order/<farmer>", methods=["POST"])
def send_order(farmer):
    if session.get("farmer") != farmer:
        return redirect(url_for("login"))

    route = ROUTES[farmer]

    send_mission(
        route["from"],
        route["area"],
        route["problem"],
        owner=farmer
    )

    return redirect(url_for("map_page", farmer=farmer))


@app.route("/map/<farmer>")
def map_page(farmer):
    if session.get("farmer") != farmer:
        return redirect(url_for("login"))

    return render_template("index.html", farmer=farmer)


@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    return render_template("admin.html")


@app.route("/admin/send_mission", methods=["POST"])
def admin_send_mission():
    if not session.get("admin"):
        return "Not allowed", 403

    data = request.json
    lat = data["lat"]
    lng = data["lng"]

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
        problem,
        owner="admin"
    )

    return "OK"


@app.route("/get_drones/<farmer>")
def get_drones_for_farmer(farmer):
    if session.get("farmer") != farmer:
        return jsonify({})

    drones = {}

    for key in r.keys("drone:*"):
        data = r.get(key)

        if not data:
            continue

        d = json.loads(data)

        if d.get("owner") == farmer:
            drones[d["id"]] = d

    return jsonify(drones)


@app.route("/get_all_drones")
def get_all_drones():
    if not session.get("admin"):
        return jsonify({})

    drones = {}

    for key in r.keys("drone:*"):
        data = r.get(key)

        if not data:
            continue

        d = json.loads(data)
        drones[d["id"]] = d

    return jsonify(drones)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)