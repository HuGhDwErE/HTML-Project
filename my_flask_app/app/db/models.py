from app.db.db import db

class User(db.Model):
    __tablename__ = "users"
    
    id = db.column(db.integer, primary_key=True)
    username = db.column(db.string(80), unique=True, nullable=False)
    password_hash = db.column(db.string(255), nullable=False)