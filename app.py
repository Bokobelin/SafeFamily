from flask import Flask, jsonify

from auth import auth_bp
from extensions import db, jwt
from models import User
from users import user_bp


def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/users")

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()

    @jwt.additional_claims_loader
    def add_claims_to_access_token(identity):
        if identity == "8cef99b8-53fb-4a32-9705-06984e97c3e9":
            return {"is_admin": "admin"}
        return {"is_admin": "user"}

    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"msg": "Token has expired", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def my_invalid_token_callback(error):
        return jsonify({"msg": "Invalid token", "error": "invalid_token"}), 401

    @jwt.unauthorized_loader
    def my_unauthorized_callback(error):
        return jsonify({"msg": "Missing token", "error": "authorization_required"}), 401

    return app
