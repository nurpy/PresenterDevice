#!/bin/bash
# Launch Flask app with environment variables
export FLASK_HOST=192.168.4.1
export FLASK_PORT=80
export DB_PATH=./data.sqlite          # default
export CSV_PATH=./submissions.csv     # default
export ADMIN_TOKEN=supersecret123     # change this before deploying

#firefox --kiosk "http://localhost/admin" &
#.venv/bin/python3 app.py &
#source .venv/bin/activate
sudo python app.py &
#sleep 5
chromium --kiosk "http://localhost/admin" &

echo "Flask app started with the following settings:"
echo "Host: $FLASK_HOST"
echo "Port: $FLASK_PORT"
echo "Database Path: $DB_PATH"
echo "CSV Path: $CSV_PATH"
