from backend.app.db import db
from backend.app.models.user import User


class AuthService:

    @staticmethod
    def authenticate(email, password):
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            return user
        return None



    @staticmethod
    def register(username, email, password):
        user = User.query.filter_by(email=email).first()
        if user:
            raise ValueError("Email is already registered")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        new_user = User(username = username, email = email)
        new_user.password = password
        db.session.add(new_user)
        db.session.commit()
        return new_user