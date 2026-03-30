from flask import Flask, request, render_template, redirect, url_for
from controller import send_mission

app = Flask(__name__)
app.secret_key = "superhemligt123"  # används för sessioner om ni vill senare

# Exempel på lantbrukare med lösenord
FARMERS = {
    "anna": {"password": "pass123", "from": (13.2005, 55.7059), "to": (13.2100, 55.7100)},
    "erik": {"password": "erikpwd", "from": (13.1900, 55.7000), "to": (13.2200, 55.7200)},
    "lisa": {"password": "lisapwd", "from": (13.1800, 55.6950), "to": (13.2300, 55.7300)}
}

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

@app.route('/order/<farmer>')
def order_page(farmer):
    coords = FARMERS[farmer]
    return render_template('order.html', farmer=farmer, coords=coords)

@app.route('/send_order/<farmer>', methods=['POST'])
def send_order(farmer):
    coords = FARMERS[farmer]
    send_mission(coords["from"], coords["to"])
    return f"Drone sent to {farmer}"

if __name__ == '__main__':
    app.run(port=5000, debug=True)
