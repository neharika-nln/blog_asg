from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()   # database schema migrations k liye
jwt = JWTManager()
bcrypt = Bcrypt()

# Blocklist for revoked tokens (in-memory for now)
jwt_blocklist = set()
