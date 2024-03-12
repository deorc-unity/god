from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'relatedToHbbb1234oPppWea' #Encrypt or secure cookies or session data
    #app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    #app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://wockoplapcfwxx:4f9434fb85c87b1cac968fbec83bd4aeca636b0e491e60e178c877e2237235eb@ec2-3-230-24-12.compute-1.amazonaws.com:5432/d3jpli3t3l6ni6"
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://nucektjuuqikvw:2340c009b4c0de865c28ddd8cd4d0434193775f7e46c331b91e80518fec2ec1b@ec2-44-218-92-155.compute-1.amazonaws.com:5432/d4920po06da314"
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Linking

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
    
