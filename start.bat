@echo off
REM Launch Flask app with environment variables

echo Flask app started with the following settings:

set FLASK_HOST=127.0.0.1
set FLASK_PORT=5000
set DB_PATH=.\data.sqlite
set CSV_PATH=.\submissions.csv
set ADMIN_TOKEN=supersecret123

echo Host: %FLASK_HOST%
echo Port: %FLASK_PORT%
echo Database Path: %DB_PATH%
echo CSV Path: %CSV_PATH%

python app.py

pause
