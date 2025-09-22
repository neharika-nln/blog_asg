from flask import jsonify
from datetime import datetime


def otp_verification(otp_store, email, otp):
    record = otp_store.get(email)
    if not record:
        return jsonify({"error": "No OTP request found"}), 400

    if record["otp"] != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    if datetime.now() > record["expires_at"]:
        return jsonify({"error": "OTP expired"}), 400

    return jsonify({"message": "OTP verified successfully"}), 200
