from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.app.services.transaction_service import TransactionService
from backend.app.services.auth_service import requires_role, get_user_role
from backend.app.models.invitation import AccountRole
from decimal import Decimal
from datetime import datetime

transaction_blueprint = Blueprint('transaction', __name__)

@transaction_blueprint.route('/api/createTransaction', methods=['POST'])
@login_required
@requires_role(AccountRole.EDITOR, AccountRole.MANAGER, AccountRole.OWNER)
def create_transaction():
    data = request.get_json()
    try:
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else None
        new_transaction = TransactionService.create_transaction(
            user=current_user,
            account_id=data['account_id'],
            category_id=data.get('category_id'),
            name=data['name'],
            amount=Decimal(data['amount']),
            date=date_obj,
            description=data.get('description'),
            currency=data.get('currency', 'EUR')
        )
        return jsonify(new_transaction.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transaction_blueprint.route('/api/updateTransaction', methods=['POST'])
@login_required
@requires_role(AccountRole.EDITOR, AccountRole.MANAGER, AccountRole.OWNER)
def update_transaction():
    data = request.get_json()
    try:
        amount = Decimal(data['amount']) if data.get('amount') is not None else None
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else None
        updated_transaction = TransactionService.update_transaction(
            user=current_user,
            transaction_id=data['transaction_id'],
            account_id=data['account_id'],
            amount=amount,
            name=data.get('name'),
            description=data.get('description'),
            category_id=data.get('category_id'),
            date=date_obj
        )
        return jsonify(updated_transaction.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transaction_blueprint.route('/api/deleteTransaction', methods=['POST'])
@login_required
@requires_role(AccountRole.EDITOR, AccountRole.MANAGER, AccountRole.OWNER)
def delete_transaction():
    data = request.get_json()
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
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search_query = request.args.get('search_query', None, type=str)
        account_id = request.args.get('account_id', None, type=int)
        category_id = request.args.get('category_id', None, type=int)

        paginated_transactions = TransactionService.get_all_transactions(
            user=current_user, 
            page=page, 
            per_page=per_page,
            search_query=search_query,
            account_id=account_id,
            category_id=category_id
        )
        
        return jsonify({
            "transactions": [t.to_dict() for t in paginated_transactions.items],
            "total_pages": paginated_transactions.pages,
            "current_page": paginated_transactions.page,
            "total_items": paginated_transactions.total
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transaction_blueprint.route('/api/getTransactionsByAccount', methods=['GET'])
@login_required
def get_transactions_by_account():
    account_id = request.args.get('account_id', type=int)
    if not account_id:
        return jsonify({"error": "Missing account_id parameter"}), 400
    
    user_role = get_user_role(current_user.id, account_id)
    if not user_role:
        return jsonify({"message": "Forbidden: You do not have access to this account."}), 403

    try:
        transactions = TransactionService.get_all_transactions_by_account(
            user=current_user,
            account_id=account_id
        )
        return jsonify([t.to_dict() for t in transactions]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 403
