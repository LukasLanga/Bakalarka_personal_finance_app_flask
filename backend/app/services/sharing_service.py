from sqlalchemy import text
from ..models.invitation import AccountRole, AccountInvitation, InvitationStatus
from ..db import db
import secrets
from datetime import datetime, timedelta

def get_user_roles(user_id):
    """Get all roles for a user across all their accounts."""
    query = text("""
        SELECT account_id, role
        FROM user_account_access
        WHERE user_id = :user_id
    """)
    results = db.session.execute(query, {"user_id": user_id}).fetchall()
    return {str(row[0]): row[1] for row in results}

def create_invitation(account_id, invited_by_user, invited_email, role):
    """Creates and stores a new account invitation."""
    if role == AccountRole.OWNER.value:
        raise ValueError("The 'Owner' role cannot be assigned to another user.")
        
    invited_email = invited_email.lower()
    
    if role not in [r.value for r in AccountRole]:
        raise ValueError(f"Invalid role. Must be one of: {[r.value for r in AccountRole]}")

    if invited_email == invited_by_user.email.lower():
        raise ValueError("You cannot invite yourself to an account.")

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=7)

    query = text("""
        INSERT INTO account_invitations (account_id, invited_by_user_id, invited_email, role, token, expires_at, status)
        VALUES (:account_id, :user_id, :email, :role, :token, :expires_at, :status)
    """)
    
    db.session.execute(query, {
        "account_id": account_id,
        "user_id": invited_by_user.id,
        "email": invited_email,
        "role": role,
        "token": token,
        "expires_at": expires_at,
        "status": "pending"
    })
    
    db.session.commit()
    return token

def accept_invitation(token, user):
    """Accepts an invitation and adds user to the account."""
    invitation = AccountInvitation.query.filter_by(token=token).first()

    if not invitation:
        raise ValueError("Invalid or expired invitation token.")

    if datetime.now() > invitation.expires_at:
        raise ValueError("Invitation has expired.")
    
    if invitation.status != InvitationStatus.PENDING.value:
        raise ValueError(f"This invitation has already been {invitation.status}.")

    if invitation.invited_email != user.email.lower():
        raise PermissionError("This invitation is for a different user.")

    insert_query = text("""
        INSERT INTO user_account_access (user_id, account_id, role)
        VALUES (:user_id, :account_id, :role)
        ON CONFLICT (user_id, account_id) DO UPDATE SET role = EXCLUDED.role;
    """)
    db.session.execute(insert_query, {"user_id": user.id, "account_id": invitation.account_id, "role": invitation.role})

    invitation.status = InvitationStatus.ACCEPTED.value
    db.session.commit()

def decline_invitation(token, user):
    """Declines an invitation."""
    invitation = AccountInvitation.query.filter_by(token=token).first()

    if not invitation:
        raise ValueError("Invalid invitation token.")
    
    if invitation.invited_email != user.email.lower():
        raise PermissionError("This invitation is for a different user.")
        
    if invitation.status != InvitationStatus.PENDING.value:
        raise ValueError(f"This invitation has already been {invitation.status}.")

    invitation.status = InvitationStatus.DECLINED.value
    db.session.commit()

def get_pending_invitations(user, status_filter):
    """Gets all pending invitations for a user."""
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
        WHERE i.invited_email = :email AND i.status = :status_filter AND i.expires_at > NOW()
        ORDER BY i.created_at DESC;
    """)
    
    results = db.session.execute(query, {"email": user.email.lower(), "status_filter": status_filter}).fetchall()
    
    return [
        {
            "id": row[0],
            "token": row[1],
            "account_name": row[2],
            "invited_by": row[3],
            "role": row[4]
        }
        for row in results
    ]

def get_account_users(account_id):
    """Gets all users with access to a specific account."""
    query = text("""
        SELECT u.id, u.username, u.email, uaa.role
        FROM user_account_access uaa
        JOIN users u ON uaa.user_id = u.id
        WHERE uaa.account_id = :account_id
        ORDER BY u.username;
    """)
    results = db.session.execute(query, {"account_id": account_id}).fetchall()
    return [{"id": r[0], "username": r[1], "email": r[2], "role": r[3]} for r in results]

def update_user_role(account_id, user_id, new_role, requester_role):
    """Updates a user's role for an account."""
    if new_role == AccountRole.OWNER.value:
        raise ValueError("The 'Owner' role cannot be assigned to another user.")

    if not new_role or new_role not in [role.value for role in AccountRole]:
        raise ValueError("Invalid role specified.")

    target_user_role_query = text("SELECT role FROM user_account_access WHERE user_id = :user_id AND account_id = :account_id")
    target_role = db.session.execute(target_user_role_query, {"user_id": user_id, "account_id": account_id}).scalar()

    if target_role == AccountRole.OWNER.value:
        raise PermissionError("The owner's role cannot be changed.")

    if requester_role == AccountRole.MANAGER:
        if target_role == AccountRole.OWNER.value:
            raise PermissionError("Managers cannot change the role of an owner.")

    query = text("UPDATE user_account_access SET role = :role WHERE user_id = :user_id AND account_id = :account_id")
    db.session.execute(query, {"role": new_role, "user_id": user_id, "account_id": account_id})
    db.session.commit()

def remove_user_from_account(account_id, user_id_to_remove, requester_id):
    """Removes a user's access from an account."""
    is_self_removal = requester_id == user_id_to_remove

    if not is_self_removal:
        from ..services.auth_service import get_user_role
        requester_role = get_user_role(requester_id, account_id)
        if not requester_role or requester_role not in [AccountRole.MANAGER, AccountRole.OWNER]:
            raise PermissionError("Forbidden: You do not have permission to remove other users.")

        target_user_role_query = text("SELECT role FROM user_account_access WHERE user_id = :user_id AND account_id = :account_id")
        target_role = db.session.execute(target_user_role_query, {"user_id": user_id_to_remove, "account_id": account_id}).scalar()

        if target_role == AccountRole.OWNER.value:
            raise ValueError("Cannot remove the owner from the account.")
        
        if requester_role == AccountRole.MANAGER and target_role == AccountRole.MANAGER.value:
            raise PermissionError("Managers cannot remove other managers.")

    query = text("DELETE FROM user_account_access WHERE user_id = :user_id AND account_id = :account_id")
    db.session.execute(query, {"user_id": user_id_to_remove, "account_id": account_id})
    db.session.commit()
    
    return is_self_removal
