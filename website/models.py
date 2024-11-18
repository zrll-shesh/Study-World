from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    point = db.Column(db.Integer, nullable=False, default=0)
    admin = db.Column(db.Boolean, nullable=False, default=False)

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Class = db.Column(db.String(150), nullable=False)
    Course = db.Column(db.String(150), nullable=False)
    Module = db.Column(db.String(150), nullable=False)
    Creator = db.Column(db.String(150), db.ForeignKey('user.username'), nullable=False)
    Created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    Visit_count = db.Column(db.Integer, nullable=False, default=0)

