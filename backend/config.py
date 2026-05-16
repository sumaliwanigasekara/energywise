import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://energywise:energywise@db/energywise",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@energywise.lk")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@123")