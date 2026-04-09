import pytest
from unittest.mock import patch, MagicMock
from backend.app.db import db
from backend.app.models.psd2_connection import Psd2Connection
from datetime import datetime, timedelta

# Sample response from the KB API for available accounts
SAMPLE_KB_ACCOUNTS_RESPONSE = {
    "accounts": [
        {
            "id": "kb-acc-1",
            "identification": {"iban": "CZ1111"},
            "currency": "CZK",
            "name": "My KB Account 1"
        },
        {
            "id": "kb-acc-2",
            "identification": {"iban": "CZ2222"},
            "currency": "EUR",
            "name": "My KB Account 2"
        },
        {
            "id": "kb-acc-3",
            "identification": {"iban": "CZ3333"},
            "currency": "CZK",
            "name": "Already Linked Account"
        }
    ]
}

SAMPLE_KB_TOKEN_RESPONSE = {
    "access_token": "new-access-token",
    "refresh_token": "new-refresh-token",
    "expires_in": 3600
}

@pytest.fixture
def setup_kb_connection(auth, test_app):
    """Fixture to create a master KB PSD2 connection for the user."""
    with test_app.app_context():
        connection = Psd2Connection(
            user_id=auth.user.id,
            bank_name='KB',
            account_id=None,
            access_token='fake-access-token',
            refresh_token='fake-refresh-token',
            token_expires_at=datetime.utcnow() + timedelta(hours=1),
            client_id='CZ3333_CZK'
        )
        db.session.add(connection)
        db.session.commit()
        yield connection

def test_get_connection_status_false(auth):
    """Test that connection status is false when no connection exists."""
    response = auth.client.get('/api/psd2-connections/status')
    assert response.status_code == 200
    assert response.get_json()['connected'] is False

def test_get_connection_status_true(auth, setup_kb_connection):
    """Test that connection status is true when a connection exists."""
    response = auth.client.get('/api/psd2-connections/status')
    assert response.status_code == 200
    assert response.get_json()['connected'] is True

@patch('backend.app.routes.kb_routes.requests.post')
@patch('backend.app.routes.kb_routes._get_kb_certs')
def test_get_kb_token_initial(mock_get_certs, mock_requests_post, auth, test_app):
    """Test the initial token acquisition and creation of a master connection."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = SAMPLE_KB_TOKEN_RESPONSE
    mock_requests_post.return_value = mock_response
    mock_get_certs.return_value = ('cert_path', 'key_path')

    response = auth.client.post('/api/psd2-connections')
    assert response.status_code == 200
    assert "master connection successful" in response.get_json()['message']

    with test_app.app_context():
        connection = Psd2Connection.query.filter_by(user_id=auth.user.id, bank_name='KB', account_id=None).first()
        assert connection is not None
        assert connection.access_token == "new-access-token"

@patch('backend.app.routes.kb_routes.sync_single_kb_account')
@patch('backend.app.routes.kb_routes.get_valid_kb_token_for_user')
def test_sync_single_account_route(mock_get_token, mock_sync_service, auth, test_app):
    """Test that the sync route correctly calls the underlying service."""
    mock_get_token.return_value = 'valid-token'
    mock_sync_service.return_value = {"id": "synced-acc-1", "name": "Synced Account"}
    
    kb_account_data = {"id": "acc-to-sync", "name": "Account to Sync"}
    
    response = auth.client.post('/api/psd2-connections/sync', json=kb_account_data)
    
    assert response.status_code == 200
    assert "Account synchronized successfully" in response.get_json()['message']
    assert response.get_json()['synced_account']['name'] == "Synced Account"
    
    # Verify the service was called correctly
    mock_get_token.assert_called_once_with(auth.user.id)
    mock_sync_service.assert_called_once_with(auth.user.id, 'valid-token', kb_account_data)

@patch('backend.app.routes.kb_routes.requests.get')
@patch('backend.app.routes.kb_routes._get_kb_certs')
def test_get_available_kb_accounts(mock_get_certs, mock_requests_get, auth, setup_kb_connection):
    """
    GIVEN a user with a valid KB connection and one linked account
    WHEN a GET request is made to /api/psd2-connections/available-accounts
    THEN the API should return only the unlinked accounts from KB.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = SAMPLE_KB_ACCOUNTS_RESPONSE
    mock_requests_get.return_value = mock_response
    mock_get_certs.return_value = ('cert_path', 'key_path')

    response = auth.client.get('/api/psd2-connections/available-accounts')
    
    assert response.status_code == 200
    available_accounts = response.get_json()
    
    assert isinstance(available_accounts, list)
    assert len(available_accounts) == 2
    
    returned_ibans = {acc['identification']['iban'] for acc in available_accounts}
    assert "CZ1111" in returned_ibans
    assert "CZ2222" in returned_ibans
    assert "CZ3333" not in returned_ibans
    
    mock_requests_get.assert_called_once()
    call_args, call_kwargs = mock_requests_get.call_args
    assert 'my/accounts' in call_args[0]
    assert 'Authorization' in call_kwargs['headers']
    assert call_kwargs['headers']['Authorization'] == 'Bearer fake-access-token'
