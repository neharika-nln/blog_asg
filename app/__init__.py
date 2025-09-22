from flask import Flask
from .config import Config     # has all the environment variables
from .extensions import db, migrate, jwt, bcrypt
from .extensions import jwt, jwt_blocklist


def create_app():     # factory function jo flask app create krte h
    app = Flask(__name__)    
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)    # connecting database and app
    migrate.init_app(app, db)
    jwt.init_app(app)   # connecting jwt manager with the app
    bcrypt.init_app(app)   # connecting bcrypt with the app


    @jwt.token_in_blocklist_loader    
    def check_if_token_revoked(jwt_header, jwt_payload: dict):
        jti = jwt_payload["jti"]  # unique identifier for the token
        return jti in jwt_blocklist   

    # Import blueprints
    from .routes.auth import auth_bp    
    from .routes.blog import blog_bp    

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(blog_bp, url_prefix="/blog")

    return app