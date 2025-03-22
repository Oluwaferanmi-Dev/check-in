import json
import os
from flask import Flask, request, jsonify, render_template
import qrcode
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore


app = Flask(__name__, template_folder="templates")


# 🔹 Ensure the QR code storage folder exists at startup
QR_CODE_FOLDER = "static/qrcodes"
if not os.path.exists(QR_CODE_FOLDER):
    os.makedirs(QR_CODE_FOLDER)
print("✅ QR Code Folder Exists or Created!")

# Ensure the templates folder exists
if not os.path.exists("templates"):
    os.makedirs("templates")

# 🔹 Load Firebase credentials from the serviceAccountKey.json file
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


@app.route("/admin")
def admin_dashboard():
    """Display the admin dashboard with visitor data."""
    checkins_ref = db.collection("checkins").stream()
    visitors = [{"id": doc.id, **doc.to_dict()} for doc in checkins_ref]
    return render_template("admin.html", visitors=visitors)


@app.route("/update_status", methods=["POST"])
def update_status():
    """Update visitor check-in status (approved/rejected)."""
    data = request.json
    visitor_id = data.get("visitor_id")
    status = data.get("status")

    if not visitor_id or status not in ["approved", "rejected"]:
        return jsonify({"error": "Invalid request"}), 400

    db.collection("checkins").document(visitor_id).update({"status": status})
    return jsonify({"message": f"Visitor {status} successfully"})


@app.route("/")
def home():
    """Default home route."""
    return "Visitor Check-In System is Running!"


@app.route("/checkin")
def checkin_form():
    """Render the visitor check-in form."""
    return render_template("checkin.html")


@app.route("/generate_qr", methods=["POST"])
def generate_qr():
    """Generate a QR code linking to the check-in form."""

    # Ensure the static/qrcodes folder exists
    if not os.path.exists(QR_CODE_FOLDER):
        os.makedirs(QR_CODE_FOLDER)

    form_url = "https://visitor-checkin.onrender.com/checkin"
    qr = qrcode.make(form_url)
    qr_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    qr_path = os.path.join(QR_CODE_FOLDER, qr_filename)
    qr.save(qr_path)

    print(f"✅ QR Code Generated: {qr_path}")  # Debugging

    return jsonify({
        "message": "QR code generated",
        "qr_code_url": f"https://visitor-checkin.onrender.com/static/qrcodes/{qr_filename}"
    })

@app.route("/submit_checkin", methods=["POST"])
def submit_checkin():
    """Process visitor check-in form submission."""
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
    
    with app.test_request_context():
        print(app.url_map)
        
    app.run(debug=True)
