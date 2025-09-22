from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Post, Comment, Like
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename
from ..services.gdrive_upload import FOLDER_ID, upload_to_drive

blog_bp = Blueprint('blog_bp', __name__)


# Create a new post
@blog_bp.route("/create", methods=["POST"])
@jwt_required()
def create_post():
    # Get form data
    title = request.form.get("title")
    content = request.form.get("content")
    user_id = get_jwt_identity()  # get current logged-in user

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400

    image_url = None
    if "image" in request.files:
        file = request.files["image"]
        filename = secure_filename(file.filename)
        os.makedirs("temp", exist_ok=True)
        temp_path = os.path.join("temp", filename)
        print(temp_path)
        file.save(temp_path)

        # upload to Google Drive
        image_url = upload_to_drive(temp_path, filename, FOLDER_ID)

        # remove temp file after upload
        os.remove(temp_path)

    new_post = Post(
        title=title,
        content=content,
        user_id=user_id,
        image=image_url
    )

    db.session.add(new_post)
    db.session.commit()

    return jsonify({
        "message": "Post created successfully", "post_id": new_post.id, "image": image_url
        }), 200


# Get all posts with likes/comments count
@blog_bp.route("/all", methods=["GET"])
def get_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    output = []
    for post in posts:
        output.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "image": post.image,
            "likes_count": len(post.likes),
            "likes": [
                {
                    "id": like.id,
                    "author_id": like.user_id
                }
                for like in post.likes
            ],
            "comments_count": len(post.comments),
            "comments": [
                {
                    "id": c.id,     # comment id
                    "content": c.content,    # comment content
                    "author_id": c.user_id,  # the user who commented
                    "author_name": c.user.name,  # name of user who commented
                    "created_at": c.created_at   # time stamp of the comment
                }
                for c in post.comments
            ],
            "created_at": post.created_at,
            "author_id": post.user_id,    # the user who posted
            "author_name": post.user.name  # name of the user who posted
        })
    return jsonify(output), 200


# Add comment to a post
@blog_bp.route("/comment/<int:post_id>", methods=["POST"])
@jwt_required()
def add_comment(post_id):
    data = request.get_json()
    user_id = get_jwt_identity()

    post = Post.query.get_or_404(post_id)
    if not data.get("content"):
        return jsonify({"error": "Comment content is required"}), 400

    comment = Comment(
        content=data["content"],
        user_id=user_id,
        post_id=post.id
    )
    db.session.add(comment)
    db.session.commit()

    return jsonify({"message": "Comment added"}), 200


# Like a post
@blog_bp.route("/like/<int:post_id>", methods=["POST"])
@jwt_required()
def like_post(post_id):
    user_id = get_jwt_identity()
    post = Post.query.get_or_404(post_id)

    # Prevent duplicate likes
    existing_like = Like.query.filter_by(
        user_id=user_id, post_id=post.id).first()
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({"message": "Post unliked"}), 200

    else:
        like = Like(user_id=user_id, post_id=post.id)
        db.session.add(like)
        db.session.commit()
        return jsonify({"message": "Post Liked"}), 201


# DELETE a post
@blog_bp.route("/delete/<int:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    current_user_id = get_jwt_identity()

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    if post.user_id != int(current_user_id):
        return jsonify(
            {"error": "Unauthorized - You can only delete your own posts"}), \
            403

    # delete comments
    for comment in post.comments:
        db.session.delete(comment)

    # delete likes
    for like in post.likes:
        db.session.delete(like)

    db.session.delete(post)
    db.session.commit()

    return jsonify({"message": "Post deleted successfully"}), 200


# UPDATE a post
@blog_bp.route("/update/<int:post_id>", methods=["PUT"])
@jwt_required()
def update_post(post_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    if post.user_id != int(current_user_id):
        return jsonify({
            "error": "Unauthorized - You can only update your own posts"}), \
            403

    # Update fields if provided
    if "title" in data:
        post.title = data["title"]
    if "content" in data:
        post.content = data["content"]

    db.session.commit()

    return jsonify({
        "message": "Post updated successfully",
        "post": {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at,
            "author_id": post.user_id
        }
    }), 200
