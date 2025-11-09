@echo off
REM ---------------------------
REM 1️⃣ Generate self-signed cert if missing
REM ---------------------------
if not exist cert.pem (
    echo Generating self-signed SSL certificate...
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 ^
        -keyout key.pem -out cert.pem ^
        -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=localhost"
    if %ERRORLEVEL% neq 0 (
        echo OpenSSL failed. Make sure it is installed and in PATH.
        pause
        exit /b 1
    )
    echo Certificate and key generated: cert.pem & key.pem
)

REM ---------------------------
REM 2️⃣ Set environment variables
REM ---------------------------
set FLASK_HOST=127.0.0.1
set FLASK_PORT=5000
set DB_PATH=survey.sqlite
set CSV_PATH=survey_submissions.csv
set ADMIN_TOKEN=supersecret123
set FLASK_SECRET=dev-secret

REM ---------------------------
REM 3️⃣ Start Flask server
REM ---------------------------
echo Starting Flask survey server...
python app.py
pause
