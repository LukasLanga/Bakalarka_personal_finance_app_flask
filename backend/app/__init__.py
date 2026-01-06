import os
from flask import Flask
from flask_login import LoginManager

from backend.app.db import db
from dotenv import load_dotenv
from backend.app.models import User
from backend.app.routes.auth import auth_blueprint
from backend.app.routes.account_routes import account_blueprint
load_dotenv()


login_manager = LoginManager()
def create_app():
    app = Flask(__name__)

    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise RuntimeError("DATABASE_URL missing in .env file")

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    if not app.config['SECRET_KEY']:
        raise RuntimeError("SECRET_KEY missing in .env file")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    login_manager.init_app(app)

    with app.app_context():
        from backend.app import models

    app.register_blueprint(account_blueprint)
    app.register_blueprint(auth_blueprint)

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))