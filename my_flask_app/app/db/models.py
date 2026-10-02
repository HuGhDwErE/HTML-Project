from app.db.db import db

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())


class Progress(db.Model):
    __tablename__ = "progress"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    key = db.Column(db.String(200), nullable=False)
    value = db.Column(db.String(30), nullable=False)
    __table_args__ = (db.UniqueConstraint("user_id", "key"),)
