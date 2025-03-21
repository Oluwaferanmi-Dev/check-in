from flask import Flask, request, jsonify, render_template
import qrcode
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore


app = Flask(__name__, template_folder="templates")


# Ensure the templates folder exists
if not os.path.exists("templates"):
    os.makedirs("templates")

# Initialize Firebase
firebase_credentials_path = "serviceAccountKey.json"
if not os.path.exists(firebase_credentials_path):
    raise ValueError(f"🚨 ERROR: Firebase credentials file not found at {firebase_credentials_path}")

cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Ensure QR code storage folder exists
QR_CODE_FOLDER = "static/qrcodes"
if not os.path.exists(QR_CODE_FOLDER):
    os.makedirs(QR_CODE_FOLDER)

@app.route("/")
def home():
    return "Visitor Check-In System is Running!"

@app.route("/checkin")
def checkin_form():
    return render_template("checkin.html")  # Ensure checkin.html exists in templates/

@app.route("/generate_qr", methods=["POST"])
def generate_qr():
    data = request.json
    name = data.get("name", "Unknown")
    purpose = data.get("purpose", "Visit")

    # URL where the visitor will check in
    form_url = f"https://visitor-checkin.onrender.com/checkin"

    # Generate the QR code linking to the check-in form
    qr = qrcode.make(form_url)
    qr_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    qr_path = os.path.join(QR_CODE_FOLDER, qr_filename)
    qr.save(qr_path)

    return jsonify({
        "message": "QR code generated",
        "qr_code_url": f"https://visitor-checkin.onrender.com/{qr_path}"
    })

@app.route("/submit_checkin", methods=["POST"])
def submit_checkin():
    data = request.json
    name = data.get("name")
    purpose = data.get("purpose")
    time_in = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not name or not purpose:
        return jsonify({"error": "Missing required fields"}), 400

    checkin_data = {
        "name": name,
        "purpose": purpose,
        "time_in": time_in,
        "status": "pending"
    }

    db.collection("checkins").add(checkin_data)

    return jsonify({"message": "Check-in submitted successfully", "status": "pending"})

if __name__ == "__main__":
    app.run(debug=True)


