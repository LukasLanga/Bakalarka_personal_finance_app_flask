from flask import Blueprint, request, jsonify, current_app, url_for
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from ..models.user import User
from ..models.account import Account
from ..models.category import Category
from ..models.user_account_access import UserAccountAccess
from ..models.invitation import AccountRole
from ..db import db
from .. import mail
from flask_mail import Message

auth_blueprint = Blueprint('auth', __name__)

DEFAULT_CATEGORIES = [
    {"name": "Groceries", "type": "expense"},
    {"name": "Transport", "type": "expense"},
    {"name": "Entertainment", "type": "expense"},
    {"name": "Utilities", "type": "expense"},
    {"name": "Housing", "type": "expense"},
    {"name": "Salary", "type": "income"},
]

def get_serializer(secret_key=None):
    """Get a URL-safe timed serializer."""
    if secret_key is None:
        secret_key = current_app.config['SECRET_KEY']
    return URLSafeTimedSerializer(secret_key)

@auth_blueprint.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"ERROR": "Missing email or password"}), 400

    user = User.query.filter(User.email.ilike(email)).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"ERROR": "Invalid credentials"}), 401

    login_user(user)
    return jsonify(user.to_dict()), 200

@auth_blueprint.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"OK": "Logged out"}), 200

@auth_blueprint.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"ERROR": "Missing username, email, or password"}), 400

    if User.query.filter(User.email.ilike(email)).first():
        return jsonify({"ERROR": "Email address already registered"}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"ERROR": "Username already taken"}), 400

    # 1. Create the user
    new_user = User(
        username=username,
        email=email.lower(),
        password_hash=generate_password_hash(password, method='pbkdf2:sha256')
    )
    db.session.add(new_user)
    db.session.flush()

    default_account = Account(
        name="Cash",
        balance=0.0,
        currency="EUR"
    )
    db.session.add(default_account)
    db.session.flush()


    owner_access = UserAccountAccess(
        user_id=new_user.id,
        account_id=default_account.id,
        role=AccountRole.OWNER.value
    )
    db.session.add(owner_access)

    for cat in DEFAULT_CATEGORIES:
        new_category = Category(
            user_id=new_user.id,
            name=cat["name"],
            type=cat["type"]
        )
        db.session.add(new_category)

    db.session.commit()

    login_user(new_user)
    return jsonify(new_user.to_dict()), 201

@auth_blueprint.route('/api/me', methods=['GET'])
@login_required
def me():
    return jsonify(current_user.to_dict()), 200

@auth_blueprint.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"ERROR": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        s = get_serializer()
        token = s.dumps(email, salt='password-reset-salt')
        
        # The URL to webpage
        reset_url = f"http://localhost:3000/reset-password/{token}"

        msg = Message(
            'Password Reset Request',
            recipients=[email]
        )
        msg.body = f'To reset your password, please click the following link: {reset_url}'
        mail.send(msg)

    return jsonify({"OK": "If an account with that email exists, a password reset link has been sent."}), 200

@auth_blueprint.route('/api/reset-password/<token>', methods=['POST'])
def reset_password_with_token(token):
    s = get_serializer()
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except (SignatureExpired, BadTimeSignature):
        return jsonify({"ERROR": "The password reset link is invalid or has expired."}), 400

    data = request.get_json()
    new_password = data.get('password')
    if not new_password:
        return jsonify({"ERROR": "Password is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"ERROR": "User not found."}), 404

    user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
    db.session.commit()

    return jsonify({"OK": "Your password has been updated successfully."}), 200
