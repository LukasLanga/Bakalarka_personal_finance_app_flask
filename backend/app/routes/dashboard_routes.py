from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from backend.app.services.transaction_service import TransactionService
from datetime import datetime, timedelta
from collections import defaultdict

dashboard_blueprint = Blueprint('dashboard', __name__)

@dashboard_blueprint.route('/api/dashboard/summary', methods=['GET'])
@login_required
def get_dashboard_summary():
    try:
        limit = int(request.args.get('limit', 5))
    except (ValueError, TypeError):
        limit = 5
    
    try:
        account_id = int(request.args.get('account_id')) if request.args.get('account_id') else None
    except (ValueError, TypeError):
        account_id = None

    now = datetime.now()
    try:
        year = int(request.args.get('year', now.year))
    except (ValueError, TypeError):
        year = now.year
    try:
        month = int(request.args.get('month', now.month))
    except (ValueError, TypeError):
        month = now.month

    summary_data = TransactionService.get_dashboard_summary(
        user=current_user,
        year=year,
        month=month,
        recent_transaction_limit=limit,
        account_id=account_id
    )
    
    return jsonify(summary_data), 200

@dashboard_blueprint.route('/api/dashboard/yearly-overview', methods=['GET'])
@login_required
def get_yearly_overview():
    """
    Provides data for the last 12 months of income and expenses.
    """
    try:
        account_id = int(request.args.get('account_id')) if request.args.get('account_id') else None
    except (ValueError, TypeError):
        account_id = None

    # Get the last 12 months of transactions
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    transactions = TransactionService.get_transactions_between_dates(
        user=current_user,
        start_date=start_date,
        end_date=end_date,
        account_id=account_id
    )

    # Process transactions into monthly income/expense totals
    monthly_data = defaultdict(lambda: {'income': 0, 'expenses': 0})
    for t in transactions:
        month_key = t.date.strftime('%b') # e.g., "Jan", "Feb"
        if t.amount > 0:
            monthly_data[month_key]['income'] += t.amount
        else:
            monthly_data[month_key]['expenses'] += abs(t.amount)

    ordered_months = [(end_date - timedelta(days=30 * i)).strftime('%b') for i in range(12)]
    ordered_months.reverse()

    chart_data = []
    for month in ordered_months:
        data = monthly_data[month]
        chart_data.append({
            "month": month,
            "income": data['income'],
            "expenses": data['expenses']
        })

    return jsonify(chart_data), 200
