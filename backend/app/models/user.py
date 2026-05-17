from app.extensions import db, bcrypt
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("user", "admin"), default="user", nullable=False)
    district = db.Column(db.String(100), default="Colombo")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    predictions = db.relationship("Prediction", backref="user", lazy=True, cascade="all, delete-orphan")
    bills = db.relationship("Bill", backref="user", lazy=True, cascade="all, delete-orphan")

    def __init__(self, name, email, password, role="user", district="Colombo"):
        self.name = name
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        self.role = role
        self.district = district

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "district": self.district,
            "created_at": self.created_at.isoformat(),
        }
