from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user

from backend.app.services.auth_service import AuthService

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    if not(email or password):
        return jsonify({"ERROR" : "Missing email or password"}), 400

    user = AuthService.authenticate(email, password)
    if not user:
        return jsonify({"ERROR" : "Invalid credentials"}), 401

    login_user(user)
    return jsonify(user.to_dict()), 200
    #return jsonify("OK"), 200

@auth_blueprint.route('/api/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"OK": "Logged out"}), 200

@auth_blueprint.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    try:
        new_user = AuthService.register(data['username'], data['email'], data['password'])
        login_user(new_user)
        return jsonify(new_user.to_dict()), 201
    except ValueError as e:
        return jsonify({"ERROR" : str(e)}), 400
   # except Exception as e:
   #     return jsonify({"ERROR" : "Registration failed"}), 400