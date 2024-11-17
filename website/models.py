from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

class Education_Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Class = db.Column(db.String(150), nullable=False)
    Course = db.Column(db.String(150), nullable=False)
    Module = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), db.ForeignKey('user.username'), nullable=False)

