run:
	FLASK_APP=database.py flask run --port=5001 --host=0.0.0.0 & \
	FLASK_APP=route_planner.py flask run --port=5002 --host=0.0.0.0 & \
	FLASK_APP=web.py flask run --host=0.0.0.0 & \
	wait

stop:
	pkill -f "flask run"
