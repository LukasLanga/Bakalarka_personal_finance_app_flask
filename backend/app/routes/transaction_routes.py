from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.app.services.transaction_service import TransactionService
from decimal import Decimal

transaction_blueprint = Blueprint('transaction', __name__)

@transaction_blueprint.route('/api/recent-transactions', methods=['GET'])
@login_required
def get_recent_transactions():
    try:
        limit = int(request.args.get('limit', 5))
    except (ValueError, TypeError):
        limit = 5
    
    try:
        transactions = TransactionService.get_recent_transactions(user=current_user, limit=limit)
        return jsonify([t.to_dict() for t in transactions]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transaction_blueprint.route('/api/createTransaction', methods=['POST'])
@login_required
def create_transaction():
    data = request.get_json()
    if not data or not data.get('account_id') or not data.get('amount'):
        return jsonify({"error": "Missing required fields: account_id and amount"}), 400

    try:
        new_transaction = TransactionService.create_transaction(
            user=current_user,
            account_id=data['account_id'],
            category_id=data.get('category_id'),
            name=data['name'],
            amount=Decimal(data['amount']),
            date=data.get('date'),
            description=data.get('description'),
            currency=data.get('currency', 'EUR')
        )
        return jsonify(new_transaction.to_dict()), 201
    except (ValueError, PermissionError) as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@transaction_blueprint.route('/api/deleteTransaction', methods=['POST'])
@login_required
def delete_transaction():
    data = request.get_json()
    if not data or not data.get('account_id') or not data.get('transaction_id'):
        return jsonify({"error": "Missing account_id or transaction_id"}), 400

    try:
        TransactionService.delete_transaction(
            user=current_user,
            account_id=data['account_id'],
            transaction_id=data['transaction_id']
        )
        return jsonify({"success": True, "message": "Transaction deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@transaction_blueprint.route('/api/recent-transactions', methods=['GET'])
@login_required
def get_recent_transactions():
    limit = request.args.get('limit', 5, type=int)
    try:
        transactions = TransactionService.get_recent_transactions(user=current_user, limit=limit)
        return jsonify([t.to_dict() for t in transactions]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transaction_blueprint.route('/api/getTransaction', methods=['GET'])
@login_required
def get_transaction():
    account_id = request.args.get('account_id', type=int)
    transaction_id = request.args.get('transaction_id', type=int)

    user_role = get_user_role(current_user.id, account_id)
    if not user_role:
        return jsonify({"message": "Forbidden: You do not have access to this account."}), 403

    try:
        transaction = TransactionService.get_transaction(
            user=current_user,
            account_id=account_id,
            transaction_id=transaction_id
        )
        return jsonify(transaction.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@transaction_blueprint.route('/api/getAllTransactions', methods=['GET'])
@login_required
def get_all_transactions():
    try:
        transactions = TransactionService.get_all_transactions(user=current_user)
        return jsonify([t.to_dict() for t in transactions]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transaction_blueprint.route('/api/getTransactionsByAccount', methods=['GET'])
@login_required
def get_transactions_by_account():
    account_id = request.args.get('account_id', type=int)
    if not account_id:
        return jsonify({"error": "Missing account_id parameter"}), 400

    try:
        transactions = TransactionService.get_all_transactions_by_account(
            user=current_user,
            account_id=account_id
        )
        return jsonify([t.to_dict() for t in transactions]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 403

@transaction_blueprint.route('/api/getTransactionsByCategory', methods=['GET'])
@login_required
def get_transactions_by_category():
    category_id = request.args.get('category_id', type=int)
    if not category_id:
        return jsonify({"error": "Missing category_id parameter"}), 400

    try:
        transactions = TransactionService.get_all_transactions_by_category(
            user=current_user,
            category_id=category_id
        )
        return jsonify([t.to_dict() for t in transactions]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 403
