from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from backend.app.services.account_service import AccountService

account_blueprint = Blueprint('account', __name__)

@account_blueprint.route('/api/accounts', methods=['POST'])
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

