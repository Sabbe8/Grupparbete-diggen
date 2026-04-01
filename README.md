# Grupparbete-diggen
export FLASK_APP=database.py
export FLASK_DEBUG=1
flask run --port=5001 --host 0.0.0.0

export FLASK_APP=drone.py
export FLASK_DEBUG=1
flask run --host 0.0.0.0

export FLASK_APP=route_planner.py
export FLASK_DEBUG=1
flask run --port=5002 --host 0.0.0.0

export FLASK_APP=web.py
export FLASK_DEBUG=1
flask run --host 0.0.0.0

