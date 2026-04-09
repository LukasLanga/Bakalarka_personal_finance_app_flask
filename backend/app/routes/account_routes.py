from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..services.account_service import AccountService
from ..services.auth_service import requires_role, get_user_role
from ..models.invitation import AccountRole

account_blueprint = Blueprint('account', __name__)

@account_blueprint.route('/api/accounts', methods=['GET'])
@login_required
def list_accounts():
    try:
        accounts = AccountService.list_accounts(current_user)
        return jsonify([acc.to_dict() for acc in accounts]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@account_blueprint.route('/api/accounts/<int:account_id>', methods=['PUT'])
@login_required
@requires_role(AccountRole.MANAGER, AccountRole.OWNER)
def update_account(account_id):
    data = request.get_json()
    try:
        updated_account = AccountService.update_account(
            user=current_user,
            account_id=account_id,
            name=data.get('name'),
            bank_name=data.get('bank_name'),
            currency=data.get('currency')
        )
        return jsonify(updated_account.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@account_blueprint.route('/api/accounts/<int:account_id>', methods=['DELETE'])
@login_required
@requires_role(AccountRole.OWNER)
def delete_account(account_id):
    try:
        AccountService.delete_account(user=current_user, account_id=account_id)
        return jsonify({"success": True, "message": "Account deleted successfully"}), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@account_blueprint.route('/api/accounts/<int:account_id>/balance', methods=['GET'])
@login_required
def get_account_balance(account_id):
    user_role = get_user_role(current_user.id, account_id)
    if not user_role:
        return jsonify({"message": "Forbidden: You do not have access to this account."}), 403

    try:
        balance = AccountService.get_account_balance(user=current_user, account_id=account_id)
        return jsonify({"balance": balance}), 200
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred."}), 500

@account_blueprint.route('/api/accounts/summary/total-balance', methods=['GET'])
@login_required
def get_total_balance():
    try:
        total_balance = AccountService.get_total_balance(current_user)
        return jsonify({"total_balance": total_balance}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
