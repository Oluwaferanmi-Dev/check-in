from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")  # Ensure this file exists
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route("/visitors", methods=["GET"])
def get_visitors():
    """Fetch all visitors for admin panel"""
    visitors = db.collection("visitors").stream()
    visitor_list = [{"id": v.id, **v.to_dict()} for v in visitors]
    return jsonify(visitor_list)


@app.route("/")
def home():
    """Default home route."""
    return "Visitor Check-In System is Running!"


@app.route("/approve/<visitor_id>", methods=["POST"])
def approve_visitor(visitor_id):
    """Approve a visitor"""
    visitor_ref = db.collection("visitors").document(visitor_id)
    visitor_ref.update({"status": "approved"})
    return jsonify({"message": "Visitor approved."})

@app.route("/reject/<visitor_id>", methods=["POST"])
def reject_visitor(visitor_id):
    """Reject a visitor"""
    visitor_ref = db.collection("visitors").document(visitor_id)
    visitor_ref.update({"status": "rejected"})
    return jsonify({"message": "Visitor rejected."})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
