import os
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, request, render_template, redirect
from werkzeug.utils import secure_filename
from datetime import datetime

# --------------------------
# 1️⃣ Create Flask app
# --------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")  # for session/flash

# --------------------------
# 2️⃣ Configuration for file uploads
# --------------------------
ACTIVE_MODE_FILE = Path("active_mode.txt")
DEFAULT_MODE = "survey"  # fallback if file missing

RESUME_UPLOAD_FOLDER = Path("uploads")
RESUME_UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_RESUME_EXTENSIONS = {"pdf", "doc", "docx", "txt"}

def allowed_resume(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_RESUME_EXTENSIONS

# --------------------------
# 3️⃣ Database helper functions
# --------------------------
def ensure_applicant_db():
    conn = sqlite3.connect("job_applications.sqlite")
    conn.execute('''
    CREATE TABLE IF NOT EXISTS applicants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        email TEXT,
        phone TEXT,
        position TEXT,
        experience TEXT,
        skills TEXT,
        resume_path TEXT,
        client_ip TEXT,
        user_agent TEXT,
        created_at TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

    # CSV backup
    csv_path = Path("job_applications.csv")
    if not csv_path.exists():
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("id,full_name,email,phone,position,experience,skills,resume_path,client_ip,user_agent,created_at\n")

def insert_applicant(data, client_ip, user_agent):
    created_at = datetime.utcnow().isoformat() + "Z"
    conn = sqlite3.connect("job_applications.sqlite")
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO applicants (
            full_name,email,phone,position,experience,skills,resume_path,client_ip,user_agent,created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("full_name"), data.get("email"), data.get("phone"), data.get("position"),
        data.get("experience"), data.get("skills"), data.get("resume_path"),
        client_ip, user_agent, created_at
    ))
    rowid = cur.lastrowid
    conn.commit()
    conn.close()

    # Append to CSV
    with open("job_applications.csv", "a", encoding="utf-8") as f:
        line = f'{rowid},"{data.get("full_name")}","{data.get("email")}","{data.get("phone")}","{data.get("position")}","{data.get("experience")}","{data.get("skills")}","{data.get("resume_path")}","{client_ip}","{user_agent}",{created_at}\n'
        f.write(line)

def get_active_mode():
    if ACTIVE_MODE_FILE.exists():
        return ACTIVE_MODE_FILE.read_text().strip()
    return DEFAULT_MODE

def set_active_mode(mode):
    ACTIVE_MODE_FILE.write_text(mode.strip())

# --------------------------
# 4️⃣ Routes
# --------------------------

@app.route("/generate_204")
@app.route("/hotspot-detect.html")
@app.route("/ncsi.txt")
@app.route("/connecttest.txt")
@app.route("/success.txt")
@app.route("/connectivity-check.html")
@app.route("/check_network_status.txt")
@app.route("/index.html")
@app.route("/generate204")
@app.route("/connectivity-check.ubuntu.com")
@app.route("/redirect")
def captive_probe():
    return redirect("http://192.168.4.1", code=302)

# Survey Page
@app.route("/survey", methods=["GET"])
def survey_form():
    return render_template("survey.html")

# Optional: handle survey submission
@app.route("/submit-survey", methods=["POST"])
def submit_survey():
    # Collect survey form data
    data = {key: (request.form.get(key) or "").strip() for key in request.form}

    # You can store survey data in a CSV or database
    csv_path = Path("survey_submissions.csv")
    if not csv_path.exists():
        with open(csv_path, "w", encoding="utf-8") as f:
            # header: adjust based on your survey questions
            f.write(",".join(data.keys()) + "\n")

    with open(csv_path, "a", encoding="utf-8") as f:
        # basic CSV write
        f.write(",".join(data.values()) + "\n")

    return render_template("survey_thankyou.html")
    
@app.route("/apply", methods=["GET"])
def job_form():
    # Show the job application form
    return render_template("job_application.html")

@app.route("/apply", methods=["POST"])
def submit_application():
    # Collect form data
    data = {key: (request.form.get(key) or "").strip() for key in request.form}

    # Handle file upload
    uploaded_file = request.files.get("resume")
    if uploaded_file and allowed_resume(uploaded_file.filename):
        filename = secure_filename(uploaded_file.filename)
        # prepend timestamp to avoid overwriting
        filename = f"{int(datetime.utcnow().timestamp())}_{filename}"
        filepath = RESUME_UPLOAD_FOLDER / filename
        uploaded_file.save(filepath)
        data["resume_path"] = str(filepath)
    else:
        data["resume_path"] = None

    client_ip = request.remote_addr or "unknown"
    user_agent = request.headers.get("User-Agent", "")
    insert_applicant(data, client_ip, user_agent)

    return render_template("job_thankyou.html")

@app.route("/main", methods=["GET"])
def index():
    return render_template("index.html", datetime=datetime)

# Captive portal root: dynamically serves whichever mode is active
@app.route("/", methods=["GET"])
def portal_home():
    mode = get_active_mode()
    if mode == "apply":
        return render_template("job_application.html")
    else:
        return render_template("survey.html")

# Admin page to toggle modes
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    current_mode = get_active_mode()
    if request.method == "POST":
        new_mode = request.form.get("mode")
        if new_mode in ["apply", "survey"]:
            set_active_mode(new_mode)
        current_mode = get_active_mode()

    return render_template("admin.html", mode=current_mode)

# --------------------------
# 5️⃣ Main
# --------------------------
if __name__ == "__main__":
    ensure_applicant_db()
    # Listen on all interfaces for Pi usage
    cert_file = Path("cert.pem")
    key_file = Path("key.pem")
    if cert_file.exists() and key_file.exists():
        print(f"Starting HTTPS Flask server on 0.0.0.0:5000")
        app.run(host="0.0.0.0", port=443, debug=True, ssl_context=('cert.pem','key.pem'))
    else:
        print("Starting HTTP Flask server (cert.pem/key.pem not found)")
        app.run(host="0.0.0.0", port=80, debug=True)

