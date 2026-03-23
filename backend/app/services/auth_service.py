from functools import wraps
from flask import jsonify, request, g
from flask_login import current_user
from sqlalchemy import text
from ..models.invitation import AccountRole
from ..db import db

def get_user_role(user_id: int, account_id: int) -> AccountRole | None:
    """Fetches the role of a user for a specific account."""
    if not user_id or not account_id:
        return None
    query = text("SELECT role FROM user_account_access WHERE user_id = :user_id AND account_id = :account_id")
    result = db.session.execute(query, {"user_id": user_id, "account_id": account_id}).fetchone()
    
    if result:
        return AccountRole(result[0])
    return None

def requires_role(*roles: AccountRole):
    """
    A decorator that enforces role-based access.
    It checks if the logged-in user has one of the required roles for an account.
    The account_id is retrieved from URL keyword arguments or the JSON request body.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"message": "Authentication required."}), 401
            
            account_id = None
            if 'account_id' in kwargs:
                account_id = kwargs['account_id']
            elif request.is_json:
                data = request.get_json()
                if 'account_id' in data:
                    account_id = data.get('account_id')

            if not account_id:
                return jsonify({"message": "This request requires an 'account_id' in the URL or JSON body."}), 400

            user_role = get_user_role(current_user.id, account_id)
            g.user_role = user_role

            if not user_role or user_role not in roles:
                return jsonify({"message": "Forbidden: You do not have the required permissions for this account."}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
