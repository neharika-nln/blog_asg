from flask import jsonify
import re
from ..models import User


def validate(email, username, password):
    # --- Email validation ---
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_pattern, email):
        return jsonify({"error": "Invalid email format"}), 400

    # --- Username rules ---
    if len(username) < 3:
        return jsonify(
            {"error": "Username must be at least 3 characters"}), 400

    # ---Password validation---
    if password == "":
        return jsonify({"error": "Password cannot be empty"}), 400

    # --- Password rules ---
    if len(password) < 6:
        return jsonify(
            {"error": "Password must be at least 6 characters"}), 400
    if password.isnumeric():
        return jsonify({"error": "Password cannot be only numbers"}), 400

    # Check if email already exists
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({"error": "Email already registered"}), 400

    # Check if username already exists
    existing_username = User.query.filter_by(username=username).first()
    if existing_username:
        return jsonify({"error": "Username already taken"}), 400

    return 200
