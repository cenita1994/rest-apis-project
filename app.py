import os
import secrets

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from db import db
from blocklist import BLOCKLIST
import models


from resources.item import blp as itemblueprint
from resources.store import blp as storeblueprint
from resources.tag import blp as tagblueprint
from resources.user import blp as userblueprint


jwt = JWTManager()   # ← create here globally


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return (
        jsonify({"message": "The token has been revoked.", "error": "token_revoked"}),
        401,
    )

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {
                "message": "The token is not fresh.",
                "error": "fresh_token_required",
            }
        ),
        401,
    )

@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == "1":      # 1 is admin
        return {"is_admin": True}
    return {"is_admin": False}


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return (
        jsonify({"message": "The token has expired.", "error": "token_expired"}),
        401,
    )


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify({"message": "Signature verification failed.", "error": "invalid_token"}),
        401,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify({"message": "Request does not contain an access token."}),
        401,
    )


def create_app(db_url=None):
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = "jose"

    # ✅ REQUIRED for logout to work
    app.config["JWT_BLACKLIST_ENABLED"] = True
    app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]

    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)
    api = Api(app)

#    with app.app_context():
#        db.create_all()

    api.register_blueprint(itemblueprint)
    api.register_blueprint(storeblueprint)
    api.register_blueprint(tagblueprint)
    api.register_blueprint(userblueprint)

    return app
