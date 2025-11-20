from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from backend.app.services.account_service import AccountService

account_blueprint = Blueprint('account', __name__)

@account_blueprint.route('/api/createAccount', methods=['POST'])
@login_required
def create_account():
    data = request.get_json()
    try:
        new_account = AccountService.create_account(
            user=current_user,
            name=data.get('name'),
            balance=data.get('balance', 0.0),
            bank_name=data.get('bank_name'),
            currency=data.get('currency', 'EUR')
        )
        return jsonify(new_account.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@account_blueprint.route('/api/deleteAccount', methods=['POST'])
@login_required
def delete_account():
    data = request.get_json()
    result = AccountService.delete_account(
        user=current_user,
        account_id=data.get('account_id')
        )
    if result:
        return jsonify({"success": True}), 200

    return jsonify({"success": False}), 400

@account_blueprint.route('/api/addAccountUser', methods=['POST'])
@login_required
def add_user():
    data = request.get_json()
    result = AccountService.add_user(
        user=current_user,
        account_id=data.get('account_id'),
        email=data.get('email'),
        role=data.get('role'),
        )
    if result:
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400


@account_blueprint.route('/api/removeAccountUser', methods=['POST'])
@login_required
def remove_user():
    data = request.get_json()
    result = AccountService.remove_user(
        user=current_user,
        account_id=data.get('account_id'),
        email=data.get('email')
    )
    if result:
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400

@account_blueprint.route('/api/listAccountUsers', methods=['POST'])
@login_required
def list_users():
    data = request.get_json()
    result = AccountService.list_users(
        user=current_user,
        account_id=data.get('account_id')
    )

    user_list = [{
        "id": user.id,
        "email": user.email,
        "name": user.name
    } for user in result]

    if result:
        return jsonify({"users": user_list}), 200
    return jsonify({"success": False}), 400

@account_blueprint.route('/api/getAccountBalance', methods=['GET'])
@login_required
def get_account_balance():
    data = request.get_json()
    result = AccountService.get_account_balance(
        user=current_user,
        account_id=data.get('account_id')
    )
    if result:
        return jsonify({"success": True, "balance": result}), 200
    return jsonify({"success": False}), 400