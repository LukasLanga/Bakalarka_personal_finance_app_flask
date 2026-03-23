import os
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from backend.app.db import db
from dotenv import load_dotenv
from backend.app.models import User

load_dotenv()

login_manager = LoginManager()
mail = Mail()

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    if test_config is None:
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            raise RuntimeError("DATABASE_URL missing in .env file")

        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            raise RuntimeError("SECRET_KEY missing in .env file")

        app.config.from_mapping(
            SECRET_KEY=secret_key,
            SQLALCHEMY_DATABASE_URI=db_url,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            # Flask-Mail configuration
            MAIL_SERVER=os.environ.get('MAIL_SERVER'),
            MAIL_PORT=int(os.environ.get('MAIL_PORT', 587)),
            MAIL_USE_TLS=os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1'],
            MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
            MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
            MAIL_DEFAULT_SENDER=os.environ.get('MAIL_USERNAME')
        )
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from backend.app.routes.auth import auth_blueprint
        from backend.app.routes.account_routes import account_blueprint
        from backend.app.routes.dashboard_routes import dashboard_blueprint
        from backend.app.routes.category_routes import category_blueprint
        from backend.app.routes.transaction_routes import transaction_blueprint
        from backend.app.routes.sharing import bp as sharing_blueprint
        from backend.app.routes.kb_routes import kb_blueprint

        # Register all blueprints
        app.register_blueprint(account_blueprint)
        app.register_blueprint(auth_blueprint)
        app.register_blueprint(dashboard_blueprint)
        app.register_blueprint(category_blueprint)
        app.register_blueprint(transaction_blueprint)
        app.register_blueprint(sharing_blueprint)
        app.register_blueprint(kb_blueprint)

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
