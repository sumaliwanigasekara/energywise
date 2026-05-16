import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env BEFORE importing config
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from flask import Flask
from config import Config
from app.extensions import db, jwt, bcrypt, cors


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    from app.routes.auth import auth_bp
    from app.routes.predict import predict_bp
    from app.routes.weather import weather_bp
    from app.routes.history import history_bp
    from app.routes.bills import bills_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(predict_bp, url_prefix="/api")
    app.register_blueprint(weather_bp, url_prefix="/api")
    app.register_blueprint(history_bp, url_prefix="/api")
    app.register_blueprint(bills_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    with app.app_context():
        db.create_all()
        _seed_admin(app)

    return app


def _seed_admin(app):
    from app.models.user import User
    admin_email = app.config["ADMIN_EMAIL"]
    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            name="Administrator",
            email=admin_email,
            password=app.config["ADMIN_PASSWORD"],
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
