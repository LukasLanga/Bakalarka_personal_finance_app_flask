from flask import Blueprint, request, jsonify, g
from flask_login import login_required, current_user
from ..services.auth_service import requires_role, get_user_role
from ..models.invitation import AccountRole
from ..services import sharing_service

bp = Blueprint('sharing', __name__)

@bp.route('/api/me/roles', methods=['GET'])
@login_required
def get_user_roles_route():
    """Get all roles for the current user across all their accounts."""
    roles = sharing_service.get_user_roles(current_user.id)
    return jsonify(roles), 200

@bp.route('/api/accounts/<int:account_id>/invitations', methods=['POST'])
@login_required
@requires_role(AccountRole.MANAGER, AccountRole.OWNER)
def invite_user_route(account_id):
    """Invite a user to an account."""
    data = request.get_json()
    invited_email = data.get('invited_email')
    role = data.get('role')

    if not invited_email or not role:
        return jsonify({"message": "Invalid data: invited_email and role are required."}), 400
    
    try:
        token = sharing_service.create_invitation(account_id, current_user, invited_email, role)
        return jsonify({"message": "Invitation sent successfully.", "token": token}), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except PermissionError as e:
        return jsonify({"message": str(e)}), 403

@bp.route('/api/invitations/<token>/accept', methods=['POST'])
@login_required
def accept_invitation_route(token):
    """Accept an account invitation."""
    if not token:
        return jsonify({"message": "Invitation token is required."}), 400

    try:
        sharing_service.accept_invitation(token, current_user)
        return jsonify({"message": "Invitation accepted successfully."}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 404 # Or 410 for expired, 409 for status
    except PermissionError as e:
        return jsonify({"message": str(e)}), 403

@bp.route('/api/invitations/<token>/decline', methods=['POST'])
@login_required
def decline_invitation_route(token):
    """Decline an account invitation."""
    if not token:
        return jsonify({"message": "Invitation token is required."}), 400

    try:
        sharing_service.decline_invitation(token, current_user)
        return jsonify({"message": "Invitation declined."}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 404 # Or 409 for status
    except PermissionError as e:
        return jsonify({"message": str(e)}), 403

@bp.route('/api/me/invitations', methods=['GET'])
@login_required
def get_pending_invitations_route():
    """Get all pending invitations for the logged-in user."""
    status_filter = request.args.get('status', 'pending', type=str)
    invitations = sharing_service.get_pending_invitations(current_user, status_filter)
    return jsonify(invitations), 200

@bp.route('/api/accounts/<int:account_id>/users', methods=['GET'])
@login_required
def get_account_users_route(account_id):
    """Get all users with access to a specific account."""
    user_role = get_user_role(current_user.id, account_id)
    if not user_role:
        return jsonify({"message": "Forbidden: You do not have access to this account."}), 403

    users = sharing_service.get_account_users(account_id)
    return jsonify(users), 200

@bp.route('/api/accounts/<int:account_id>/users/<int:user_id>', methods=['PUT'])
@login_required
@requires_role(AccountRole.MANAGER, AccountRole.OWNER)
def update_user_role_route(account_id, user_id):
    """Update a user's role for an account."""
    data = request.get_json()
    new_role = data.get('role')

    try:
        sharing_service.update_user_role(account_id, user_id, new_role, g.user_role)
        return jsonify({"message": "User role updated successfully."}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except PermissionError as e:
        return jsonify({"message": str(e)}), 403

@bp.route('/api/accounts/<int:account_id>/users/<int:user_id>', methods=['DELETE'])
@login_required
def remove_user_from_account_route(account_id, user_id):
    """Remove a user's access from an account. Allows self-removal."""
    try:
        is_self_removal = sharing_service.remove_user_from_account(account_id, user_id, current_user.id)
        message = "You have left the account." if is_self_removal else "User removed from account successfully."
        return jsonify({"message": message}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except PermissionError as e:
        return jsonify({"message": str(e)}), 403
