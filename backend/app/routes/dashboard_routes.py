from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from backend.app.services.transaction_service import TransactionService

dashboard_blueprint = Blueprint('dashboard', __name__)

@dashboard_blueprint.route('/api/dashboardSummary', methods=['GET'])
@login_required
def get_dashboard_summary():
    try:
        limit = int(request.args.get('limit', 5))
    except (ValueError, TypeError):
        limit = 5

    summary_data = TransactionService.get_dashboard_summary(
        user=current_user,
        recent_transaction_limit=limit
    )
    
    return jsonify(summary_data), 200
