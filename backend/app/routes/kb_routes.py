
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import requests
import os
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from backend.app.db import db
from backend.app.models import Psd2Connection
from backend.app.services.kb_integration_service import sync_single_kb_account
from backend.app.services.kb_utils import _get_kb_certs

kb_blueprint = Blueprint('kb', __name__)

def _perform_token_refresh(refresh_token):
    """Internal logic to call the KB refresh token endpoint."""
    token_url = f"{os.environ.get('KB_OAUTH_URL')}/token"
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': os.environ.get('KB_CLIENT_ID'),
        'client_secret': "string",
        'redirect_uri': "string"
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    cert = _get_kb_certs()
    
    response = requests.post(token_url, headers=headers, data=payload, cert=cert)
    response.raise_for_status()
    return response.json()

def get_valid_kb_token_for_user(user_id):
    """
    Retrieves a valid KB access token for a user from the master connection record,
    refreshing it if necessary.
    """
    master_connection = Psd2Connection.query.filter_by(user_id=user_id, bank_name='KB', account_id=None).first()
    if not master_connection or not master_connection.access_token:
        raise Exception("No master KB connection with tokens found for this user.")

    if not master_connection.token_expires_at or master_connection.token_expires_at <= datetime.utcnow() + timedelta(seconds=60):
        print("Token expired or nearing expiration, refreshing...")
        refreshed_data = _perform_token_refresh(master_connection.refresh_token)
        
        master_connection.access_token = refreshed_data['access_token']
        master_connection.refresh_token = refreshed_data.get('refresh_token', master_connection.refresh_token)
        expires_in = refreshed_data.get('expires_in', 300)
        master_connection.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        db.session.commit()
        return master_connection.access_token

    return master_connection.access_token

@kb_blueprint.route('/kb/connection-status', methods=['GET'])
@login_required
def get_connection_status():
    """Checks if a master KB connection record exists for the current user."""
    master_connection = Psd2Connection.query.filter_by(user_id=current_user.id, bank_name='KB', account_id=None).first()
    is_connected = master_connection is not None and master_connection.access_token is not None
    return jsonify({'connected': is_connected})

@kb_blueprint.route('/kb/token', methods=['POST'])
@login_required
def get_kb_token():
    """
    Initial token acquisition. Creates or updates the user's master PSD2 connection.
    """
    code = os.environ.get('KB_CLIENT_ID')
    token_url = f"{os.environ.get('KB_OAUTH_URL')}/token"
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': "string",
        'client_id': os.environ.get('KB_CLIENT_ID'),
        'client_secret': "string"
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        cert = _get_kb_certs()
        response = requests.post(token_url, headers=headers, data=payload, cert=cert)
        response.raise_for_status()
        token_data = response.json()

        master_connection = Psd2Connection.query.filter_by(user_id=current_user.id, bank_name='KB', account_id=None).first()
        if not master_connection:
            master_connection = Psd2Connection(user_id=current_user.id, bank_name='KB', account_id=None)
            db.session.add(master_connection)

        master_connection.access_token = token_data['access_token']
        master_connection.refresh_token = token_data.get('refresh_token')
        expires_in = token_data.get('expires_in', 300)
        master_connection.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        db.session.commit()

        return jsonify({'message': 'KB master connection successful.'})
    except (FileNotFoundError, requests.exceptions.RequestException) as e:
        return jsonify({'error': str(e)}), 500

@kb_blueprint.route('/kb/available-accounts', methods=['GET'])
@login_required
def get_available_kb_accounts():
    """
    Fetches accounts from KB API and filters out those already linked to the user via a composite key (IBAN + Currency).
    """
    try:
        access_token = get_valid_kb_token_for_user(current_user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        cert = _get_kb_certs()
        
        base_url = os.environ.get('KB_API_BASE_URL')
        accounts_url = f"{base_url}/my/accounts"
        
        params = {'order': 'DESC'}
        response = requests.get(accounts_url, headers=headers, params=params, cert=cert)
        response.raise_for_status()
        kb_accounts = response.json().get('accounts', [])

        linked_composite_ids = {
            conn.client_id for conn in 
            Psd2Connection.query.filter(
                Psd2Connection.user_id == current_user.id,
                Psd2Connection.client_id.isnot(None)
            ).all()
        }
        
        available_accounts = []
        for acc in kb_accounts:
            iban = acc.get('identification', {}).get('iban')
            currency = acc.get('currency')
            if iban and currency:
                composite_id = f"{iban}_{currency}"
                if composite_id not in linked_composite_ids:
                    available_accounts.append(acc)
        
        return jsonify(available_accounts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kb_blueprint.route('/kb/sync-single-account', methods=['POST'])
@login_required
def sync_single_account_route():
    """
    Endpoint to trigger a sync for a single, specific KB account using its full data.
    """
    kb_account_data = request.get_json()
    if not kb_account_data or not kb_account_data.get('id'):
        return jsonify({'error': 'Full kb_account_data object is required'}), 400
        
    try:
        access_token = get_valid_kb_token_for_user(current_user.id)
        synced_account = sync_single_kb_account(current_user.id, access_token, kb_account_data)
        return jsonify({
            'message': 'Account synchronized successfully.',
            'synced_account': synced_account
        }), 200
    except Exception as e:
        print("--- ERROR IN /kb/sync-single-account ---")
        traceback.print_exc()
        print("------------------------------------")
        return jsonify({'error': str(e)}), 500

@kb_blueprint.route('/kb/accounts/<client_id>/transactions', methods=['GET'])
@login_required
def get_kb_account_transactions(client_id):
    try:
        access_token = get_valid_kb_token_for_user(current_user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        cert = _get_kb_certs()

        base_url = os.environ.get('KB_API_BASE_URL')
        transactions_url = f"{base_url}/my/accounts/{client_id}/transactions"
        
        params = request.args.to_dict()
        if 'order' not in params:
            params['order'] = 'DESC'

        response = requests.get(transactions_url, headers=headers, params=params, cert=cert)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kb_blueprint.route('/kb/accounts/<client_id>/balance', methods=['GET'])
@login_required
def get_kb_account_balance(client_id):
    try:
        access_token = get_valid_kb_token_for_user(current_user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        cert = _get_kb_certs()

        base_url = os.environ.get('KB_API_BASE_URL')
        balance_url = f"{base_url}/my/accounts/{client_id}/balance"
        params = {k: v for k, v in request.args.items()}

        response = requests.get(balance_url, headers=headers, params=params, cert=cert)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
