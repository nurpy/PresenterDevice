import os
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, request, render_template
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

# --------------------------
# 4️⃣ Routes
# --------------------------

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

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", datetime=datetime)
    
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
        app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=('cert.pem','key.pem'))
    else:
        print("Starting HTTP Flask server (cert.pem/key.pem not found)")
        app.run(host="0.0.0.0", port=5000, debug=True)

