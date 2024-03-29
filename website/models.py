from . import db 
from flask_login import UserMixin

class Linking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    custom = db.Column(db.String(10000), unique=True)
    playstore = db.Column(db.String(10000))
    appstore = db.Column(db.String(10000))
    fallback = db.Column(db.String(10000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    custom_link_clicks = db.Column(db.Integer, default=0)
    ios_redirects = db.Column(db.Integer, default=0)
    android_redirects = db.Column(db.Integer, default=0)
    fallback_redirects = db.Column(db.Integer, default=0)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    links = db.relationship('Linking')

