@app.route('/get_drones')
def get_drones():

    keys = r.keys("drone:*")

    drones = {}

    for key in keys:
        drone = json.loads(r.get(key))

        drones[drone["id"]] = {
            "x": translate(drone["longitude"]),
            "y": translate(drone["latitude"]),
            "status": drone["status"]
        }

    return drones