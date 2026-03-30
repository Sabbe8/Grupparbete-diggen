from flask import Flask, request, render_template
from controller import send_mission

app = Flask(__name__)

FARMERS = {
    "anna": {"from": (13.2005, 55.7059), "to": (13.2100, 55.7100)},
    "erik": {"from": (13.1900, 55.7000), "to": (13.2200, 55.7200)},
    "lisa": {"from": (13.1800, 55.6950), "to": (13.2300, 55.7300)}
}

@app.route('/')
def index():
    return render_template('index.html')  # ändra från inline HTML

@app.route('/order', methods=['POST'])
def order():
    data = request.json
    farmer = data['farmer']

    coords = FARMERS[farmer]
    send_mission(coords["from"], coords["to"])

    return f"Drone sent to {farmer}"

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
