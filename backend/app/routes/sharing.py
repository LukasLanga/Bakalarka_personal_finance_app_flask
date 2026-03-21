from flask import Blueprint, request, jsonify, g
from flask_login import login_required, current_user
from sqlalchemy import text
from ..services.auth_service import requires_role, get_user_role
from ..models.invitation import AccountRole, AccountInvitation, InvitationStatus
from ..db import db
import secrets
from datetime import datetime, timedelta

bp = Blueprint('sharing', __name__)

@bp.route('/api/user-roles', methods=['GET'])
@login_required
def get_user_roles():
    """Get all roles for the current user across all their accounts."""
    query = text("""
        SELECT account_id, role
        FROM user_account_access
        WHERE user_id = :user_id
    """)
    results = db.session.execute(query, {"user_id": current_user.id}).fetchall()
    roles = {str(row[0]): row[1] for row in results}
    return jsonify(roles), 200

@bp.route('/api/accounts/<int:account_id>/invitations', methods=['POST'])
@login_required
@requires_role(AccountRole.MANAGER, AccountRole.OWNER)
def invite_user(account_id):
    """Invite a user to an account."""
    data = request.get_json()
    invited_email = data.get('invited_email')
    role = data.get('role')

    if not invited_email or not role:
        return jsonify({"message": "Invalid data: invited_email and role are required."}), 400
    
    invited_email = invited_email.lower()
    
    if role not in [r.value for r in AccountRole]:
        return jsonify({"message": f"Invalid role. Must be one of: {[r.value for r in AccountRole]}"}), 400

    if invited_email == current_user.email.lower():
        return jsonify({"message": "You cannot invite yourself to an account."}), 400

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=7)

    query = text("""
        INSERT INTO account_invitations (account_id, invited_by_user_id, invited_email, role, token, expires_at, status)
        VALUES (:account_id, :user_id, :email, :role, :token, :expires_at, :status)
    """)
    
    db.session.execute(query, {
        "account_id": account_id,
        "user_id": current_user.id,
        "email": invited_email,
        "role": role,
        "token": token,
        "expires_at": expires_at,
        "status": "pending"
    })
    
    db.session.commit()
    
    return jsonify({"message": "Invitation sent successfully.", "token": token}), 201

@bp.route('/api/invitations/accept', methods=['POST'])
@login_required
def accept_invitation():
    """Accept an account invitation."""
    token = request.json.get('token')
    if not token:
        return jsonify({"message": "Invitation token is required."}), 400

    invitation = AccountInvitation.query.filter_by(token=token).first()

    if not invitation:
        return jsonify({"message": "Invalid or expired invitation token."}), 404

    if datetime.now() > invitation.expires_at:
        return jsonify({"message": "Invitation has expired."}), 410
    
    if invitation.status != InvitationStatus.PENDING.value:
        return jsonify({"message": f"This invitation has already been {invitation.status}."}), 409

    if invitation.invited_email != current_user.email.lower():
        return jsonify({"message": "This invitation is for a different user."}), 403

    insert_query = text("""
        INSERT INTO user_account_access (user_id, account_id, role)
        VALUES (:user_id, :account_id, :role)
        ON CONFLICT (user_id, account_id) DO UPDATE SET role = EXCLUDED.role;
    """)
    db.session.execute(insert_query, {"user_id": current_user.id, "account_id": invitation.account_id, "role": invitation.role})

    invitation.status = InvitationStatus.ACCEPTED.value
    db.session.commit()
    
    return jsonify({"message": "Invitation accepted successfully."}), 200

@bp.route('/api/invitations/decline', methods=['POST'])
@login_required
def decline_invitation():
    """Decline an account invitation."""
    token = request.json.get('token')
    if not token:
        return jsonify({"message": "Invitation token is required."}), 400

    invitation = AccountInvitation.query.filter_by(token=token).first()

    if not invitation:
        return jsonify({"message": "Invalid invitation token."}), 404
    
    if invitation.invited_email != current_user.email.lower():
        return jsonify({"message": "This invitation is for a different user."}), 403
        
    if invitation.status != InvitationStatus.PENDING.value:
        return jsonify({"message": f"This invitation has already been {invitation.status}."}), 409

    invitation.status = InvitationStatus.DECLINED.value
    db.session.commit()

    return jsonify({"message": "Invitation declined."}), 200

@bp.route('/api/invitations/pending', methods=['GET'])
@login_required
def get_pending_invitations():
    """Get all pending invitations for the logged-in user."""
    query = text("""
        SELECT
            i.id,
            i.token,
            a.name AS account_name,
            u.username AS invited_by,
            i.role
        FROM account_invitations i
        JOIN accounts a ON i.account_id = a.id
        JOIN users u ON i.invited_by_user_id = u.id
        WHERE i.invited_email = :email AND i.status = 'pending' AND i.expires_at > NOW()
        ORDER BY i.created_at DESC;
    """)
    
    results = db.session.execute(query, {"email": current_user.email.lower()}).fetchall()
    
    invitations = [
        {
            "id": row[0],
            "token": row[1],
            "account_name": row[2],
            "invited_by": row[3],
            "role": row[4]
        }
        for row in results
    ]
    return jsonify(invitations), 200

@bp.route('/api/accounts/<int:account_id>/users', methods=['GET'])
@login_required
def get_account_users(account_id):
    """Get all users with access to a specific account."""
    # First, verify the current user has any access to this account at all.
    user_role = get_user_role(current_user.id, account_id)
    if not user_role:
        return jsonify({"message": "Forbidden: You do not have access to this account."}), 403

    # If they have access, they can see the list of other users.
    query = text("""
        SELECT u.id, u.username, u.email, uaa.role
        FROM user_account_access uaa
        JOIN users u ON uaa.user_id = u.id
        WHERE uaa.account_id = :account_id
        ORDER BY u.username;
    """)
    results = db.session.execute(query, {"account_id": account_id}).fetchall()
    users = [{"id": r[0], "username": r[1], "email": r[2], "role": r[3]} for r in results]
    return jsonify(users), 200

@bp.route('/api/accounts/<int:account_id>/users/<int:user_id>', methods=['PUT'])
@login_required
@requires_role(AccountRole.MANAGER, AccountRole.OWNER)
def update_user_role(account_id, user_id):
    """Update a user's role for an account."""
    data = request.get_json()
    new_role = data.get('role')
    if not new_role or new_role not in [role.value for role in AccountRole]:
        return jsonify({"message": "Invalid role specified."}), 400

    # Owners cannot have their role changed by others.
    if g.user_role == AccountRole.MANAGER:
        target_user_role_query = text("SELECT role FROM user_account_access WHERE user_id = :user_id AND account_id = :account_id")
        target_role = db.session.execute(target_user_role_query, {"user_id": user_id, "account_id": account_id}).scalar()
        if target_role == AccountRole.OWNER.value:
            return jsonify({"message": "Managers cannot change the role of an owner."}), 403

    query = text("UPDATE user_account_access SET role = :role WHERE user_id = :user_id AND account_id = :account_id")
    db.session.execute(query, {"role": new_role, "user_id": user_id, "account_id": account_id})
    db.session.commit()
    return jsonify({"message": "User role updated successfully."}), 200

@bp.route('/api/accounts/<int:account_id>/users/<int:user_id>', methods=['DELETE'])
@login_required
def remove_user_from_account(account_id, user_id):
    """Remove a user's access from an account. Allows self-removal."""
    
    is_self_removal = current_user.id == user_id

    # Self-removal allowed
    if not is_self_removal:
        requester_role = get_user_role(current_user.id, account_id)
        if not requester_role or requester_role not in [AccountRole.MANAGER, AccountRole.OWNER]:
            return jsonify({"message": "Forbidden: You do not have permission to remove other users."}), 403

        target_user_role_query = text("SELECT role FROM user_account_access WHERE user_id = :user_id AND account_id = :account_id")
        target_role = db.session.execute(target_user_role_query, {"user_id": user_id, "account_id": account_id}).scalar()

        if target_role == AccountRole.OWNER.value:
            return jsonify({"message": "Cannot remove the owner from the account."}), 400
        
        if requester_role == AccountRole.MANAGER and target_role == AccountRole.MANAGER.value:
            return jsonify({"message": "Managers cannot remove other managers."}), 403

    query = text("DELETE FROM user_account_access WHERE user_id = :user_id AND account_id = :account_id")
    db.session.execute(query, {"user_id": user_id, "account_id": account_id})
    db.session.commit()
    
    message = "You have left the account." if is_self_removal else "User removed from account successfully."
    return jsonify({"message": message}), 200
