from flask import Blueprint, request, jsonify

from app.utils.generate_otp import generate_otp
from app.utils.verify_otp import otp_verification
from app.utils.validate import validate
from ..models import User, Like, Comment
from flask_jwt_extended import create_access_token, jwt_required
from flask_jwt_extended import get_jwt_identity, get_jwt
from ..extensions import db, bcrypt, jwt_blocklist
from ..services.send_email import send_otp_email

auth_bp = Blueprint("auth", __name__)

# Temporary store for OTPs (better to use Redis or DB for production)
otp_store = {}


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    required_fields = ["name", "username", "email", "password"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    username = data.get("username").strip()
    name = data.get("name").strip()
    email = data.get("email").strip().lower()
    password = data.get("password")

    if validate(email, username, password) != 200:
        return validate(email, username, password)

    hashed_password = bcrypt.generate_password_hash(
        data["password"]).decode("utf-8")

    # Create new user
    new_user = User(
        username=username,
        name=name,
        email=email,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    user = User.query.filter_by(username=data["username"]).first()
    if not user:
        return jsonify({"message": "User not found!"}), 401

    if not bcrypt.check_password_hash(user.password, data["password"]):
        return jsonify({"message": "Wrong password!"}), 401

    if user and bcrypt.check_password_hash(user.password, data["password"]):
        token = create_access_token(identity=str(user.id))
        return jsonify({
            "user_id": user.id,
            "token": token,
            "name": user.name
        }), 200


@auth_bp.route('/profile', methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    # count posts
    posts_count = len(user.posts)

    # collect all post IDs of this user
    post_ids = [post.id for post in user.posts]

    # count likes on those posts
    likes_count = Like.query.filter(Like.post_id.in_(
        post_ids)).count() if post_ids else 0

    # count comments on those posts
    comments_count = Comment.query.filter(Comment.post_id.in_(
        post_ids)).count() if post_ids else 0

    return jsonify({
        "name": user.username,
        "email": user.email,
        "posts_count": posts_count,
        "posts_likes": likes_count,
        "posts_comments": comments_count,
    })


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # token’s unique ID
    jwt_blocklist.add(jti)  # add it to the blocklist
    return jsonify({"message": "Logged out successfully"}), 200


# Step 1: Request OTP
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Email not registered"}), 404

    otp = generate_otp(otp_store, email)

    # Send OTP via SendGrid
    send_otp_email(email, otp)

    return jsonify({"message": "OTP sent to your email"}), 200


# Step 2: Verify OTP
@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")

    return otp_verification(otp_store, email, otp)


# Step 3: Reset Password
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("new_password")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Email not registered"}), 404

    # ---Password validation---
    if new_password == "":
        return jsonify({"error": "Password cannot be empty"}), 400

    # --- Password rules ---
    if len(new_password) < 6:
        return jsonify(
            {"error": "Password must be at least 6 characters"}), 400
    if new_password.isnumeric():
        return jsonify({"error": "Password cannot be only numbers"}), 400

    # Hash password before saving (important!)
    user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")

    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200
