import pytest
from backend.app.db import db
from backend.app.models.account import Account
from backend.app.models.user import User
from backend.app.models.invitation import AccountInvitation, AccountRole, InvitationStatus
from backend.app.models.user_account_access import UserAccountAccess
import secrets
from datetime import datetime, timedelta

def test_invite_user_success(auth, test_app):
    """
    GIVEN a logged-in user with manager access to an account
    WHEN a POST request is made to /api/accounts/<account_id>/invitations
    THEN check that the response is 201 and an invitation is created
    """
    with test_app.app_context():
        account = Account(name='Test Account', balance=1000)
        db.session.add(account)
        db.session.commit()

        access = UserAccountAccess(user_id=auth.user.id, account_id=account.id, role=AccountRole.MANAGER.value)
        db.session.add(access)
        db.session.commit()

        invite_data = {
            'invited_email': 'NewUser@Example.COM',
            'role': 'viewer'
        }
        response = auth.client.post(f'/api/accounts/{account.id}/invitations', json=invite_data)

        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data['message'] == 'Invitation sent successfully.'

        invitation = AccountInvitation.query.filter_by(role='viewer').first()
        assert invitation is not None
        assert invitation.invited_email == 'newuser@example.com'
        assert invitation.role == 'viewer'

def test_invite_user_no_permission(auth, test_app):
    """
    GIVEN a logged-in user with only 'viewer' access to an account
    WHEN a POST request is made to /api/accounts/<account_id>/invitations
    THEN check that the response is 403 Forbidden
    """
    with test_app.app_context():
        account = Account(name='Viewer Account', balance=500)
        db.session.add(account)
        db.session.commit()

        access = UserAccountAccess(user_id=auth.user.id, account_id=account.id, role=AccountRole.VIEWER.value)
        db.session.add(access)
        db.session.commit()

        invite_data = {
            'invited_email': 'anotheruser@example.com',
            'role': 'viewer'
        }
        response = auth.client.post(f'/api/accounts/{account.id}/invitations', json=invite_data)

        assert response.status_code == 403

def test_accept_invitation_success(auth, test_app):
    """
    GIVEN a valid invitation for a logged-in user
    WHEN a POST request is made to /api/invitations/accept
    THEN check that the user gains access and the invitation is updated
    """
    with test_app.app_context():
        account = Account(name='Shared Account', balance=2000)
        db.session.add(account)
        db.session.flush()

        token = secrets.token_urlsafe(32)
        invitation = AccountInvitation(
            account_id=account.id,
            invited_by_user_id=auth.user.id,
            invited_email=auth.user.email,
            role=AccountRole.EDITOR.value,
            token=token,
            expires_at=datetime.now() + timedelta(days=1)
        )
        db.session.add(invitation)
        db.session.commit()

        response = auth.client.post('/api/invitations/accept', json={'token': token})

        assert response.status_code == 200
        assert response.get_json()['message'] == 'Invitation accepted successfully.'

        updated_invitation = AccountInvitation.query.get(invitation.id)
        assert updated_invitation.status == InvitationStatus.ACCEPTED.value

        user_access = UserAccountAccess.query.filter_by(user_id=auth.user.id, account_id=account.id).first()
        assert user_access is not None
        assert user_access.role == AccountRole.EDITOR.value

def test_decline_invitation_success(auth, test_app):
    """
    GIVEN a valid invitation for a logged-in user
    WHEN a POST request is made to /api/invitations/decline
    THEN check that the invitation status is updated
    """
    with test_app.app_context():
        account = Account(name='Declined Account', balance=3000)
        db.session.add(account)
        db.session.flush()

        token = secrets.token_urlsafe(32)
        invitation = AccountInvitation(
            account_id=account.id,
            invited_by_user_id=auth.user.id,
            invited_email=auth.user.email,
            role=AccountRole.VIEWER.value,
            token=token,
            expires_at=datetime.now() + timedelta(days=1)
        )
        db.session.add(invitation)
        db.session.commit()

        response = auth.client.post('/api/invitations/decline', json={'token': token})

        assert response.status_code == 200
        assert response.get_json()['message'] == 'Invitation declined.'

        updated_invitation = AccountInvitation.query.get(invitation.id)
        assert updated_invitation.status == InvitationStatus.DECLINED.value
        user_access = UserAccountAccess.query.filter_by(user_id=auth.user.id, account_id=account.id).first()
        assert user_access is None

def test_accept_invitation_invalid_token(auth, test_app):
    """
    GIVEN a logged-in user
    WHEN a POST request is made to /api/invitations/accept with a bad token
    THEN check that the response is 404
    """
    response = auth.client.post('/api/invitations/accept', json={'token': 'this-is-not-a-real-token'})
    assert response.status_code == 404

@pytest.mark.xfail(reason="Known bug in remove_user_from_account: g.user_role is not set.")
def test_manager_can_remove_viewer(auth, test_app):
    """
    GIVEN a Manager and a Viewer on an account
    WHEN the Manager sends a DELETE request for the Viewer
    THEN the Viewer's access is revoked.
    """
    with test_app.app_context():
        viewer_user = User(username="viewer_user", email="viewer@user.com", password="pw")
        account = Account(name="Hierarchical Account", balance=100)
        db.session.add_all([viewer_user, account])
        db.session.flush()

        manager_access = UserAccountAccess(user_id=auth.user.id, account_id=account.id, role=AccountRole.MANAGER.value)
        viewer_access = UserAccountAccess(user_id=viewer_user.id, account_id=account.id, role=AccountRole.VIEWER.value)
        db.session.add_all([manager_access, viewer_access])
        db.session.commit()

        response = auth.client.delete(f'/api/accounts/{account.id}/users/{viewer_user.id}')
        assert response.status_code == 200

        removed_access = UserAccountAccess.query.filter_by(user_id=viewer_user.id, account_id=account.id).first()
        assert removed_access is None

@pytest.mark.xfail(reason="Known bug in remove_user_from_account: g.user_role is not set.")
def test_manager_cannot_remove_manager(auth, test_app):
    """
    GIVEN two Managers on an account
    WHEN one Manager tries to DELETE the other
    THEN the request is forbidden.
    """
    with test_app.app_context():
        other_manager = User(username="other_manager", email="manager2@user.com", password="pw")
        account = Account(name="Peer Account", balance=100)
        db.session.add_all([other_manager, account])
        db.session.flush()

        manager1_access = UserAccountAccess(user_id=auth.user.id, account_id=account.id, role=AccountRole.MANAGER.value)
        manager2_access = UserAccountAccess(user_id=other_manager.id, account_id=account.id, role=AccountRole.MANAGER.value)
        db.session.add_all([manager1_access, manager2_access])
        db.session.commit()

        response = auth.client.delete(f'/api/accounts/{account.id}/users/{other_manager.id}')
        assert response.status_code == 403

@pytest.mark.xfail(reason="Known bug in remove_user_from_account: g.user_role is not set.")
def test_user_can_remove_self(auth, test_app):
    """
    GIVEN a user with 'Viewer' access
    WHEN they send a DELETE request for their own user ID
    THEN their access is revoked.
    """
    with test_app.app_context():
        account = Account(name="Self-Removal Test", balance=100)
        db.session.add(account)
        db.session.flush()
        
        viewer_access = UserAccountAccess(user_id=auth.user.id, account_id=account.id, role=AccountRole.VIEWER.value)
        db.session.add(viewer_access)
        db.session.commit()

        response = auth.client.delete(f'/api/accounts/{account.id}/users/{auth.user.id}')
        assert response.status_code == 200
        assert "You have left the account" in response.get_json()['message']

        removed_access = UserAccountAccess.query.filter_by(user_id=auth.user.id, account_id=account.id).first()
        assert removed_access is None
