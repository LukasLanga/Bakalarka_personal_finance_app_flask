
import requests
from datetime import datetime
from ..db import db
from ..models import Account, Transaction, UserAccountAccess, Psd2Connection
from .kb_utils import _get_kb_certs
import os
from collections import defaultdict

def _create_local_account_and_link(user_id, kb_account_data):
    """Helper to create a new local account and its PSD2 connection link."""
    iban = kb_account_data.get('identification', {}).get('iban')
    currency = kb_account_data.get('currency')
    composite_id = f"{iban}_{currency}"

    print(f"--- DEBUG: Creating new local account for Composite ID: {composite_id}")
    
    account = Account(
        name=f"{kb_account_data.get('nameI18N', 'Unnamed')} ({currency})",
        bank_name=kb_account_data.get('servicer', {}).get('bankCode', 'KB'),
        currency=currency,
        balance=0
    )
    db.session.add(account)
    
    user_access = UserAccountAccess(user_id=user_id, role='owner', account=account)
    db.session.add(user_access)
    
    connection = Psd2Connection(
        user_id=user_id,
        bank_name='KB',
        client_id=composite_id,
        account=account
    )
    db.session.add(connection)
    db.session.commit()
    
    print(f"--- DEBUG: Committed new local account '{account.name}' (ID: {account.id})")
    return account

def sync_single_kb_account(user_id, access_token, kb_account_data_to_sync):
    """
    Syncs a single multi-currency account group (by IBAN) to the local database.
    """
    base_url = os.environ.get('KB_API_BASE_URL')
    headers = {'Authorization': f'Bearer {access_token}'}
    cert = _get_kb_certs()

    iban_to_sync = kb_account_data_to_sync.get('identification', {}).get('iban')
    if not iban_to_sync:
        raise Exception("IBAN not found in the provided account data.")

    accounts_url = f"{base_url}/my/accounts"
    try:
        accounts_response = requests.get(accounts_url, headers=headers, cert=cert)
        accounts_response.raise_for_status()
        all_kb_accounts = accounts_response.json().get('accounts', [])
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch accounts from KB API: {e}")

    accounts_by_iban = defaultdict(list)
    for acc in all_kb_accounts:
        iban = acc.get('identification', {}).get('iban')
        if iban:
            accounts_by_iban[iban].append(acc)

    local_accounts_map = {}
    for acc_data in accounts_by_iban.get(iban_to_sync, []):
        currency = acc_data.get('currency')
        composite_id = f"{iban_to_sync}_{currency}"
        
        connection = Psd2Connection.query.filter_by(user_id=user_id, client_id=composite_id).first()
        if connection and connection.account:
            local_accounts_map[currency] = connection.account
        else:
            newly_created_account = _create_local_account_and_link(user_id, acc_data)
            local_accounts_map[currency] = newly_created_account

    kb_session_id = accounts_by_iban[iban_to_sync][0].get('id')
    transactions_url = f"{base_url}/my/accounts/{kb_session_id}/transactions"
    try:
        params = {'order': 'DESC'}
        transactions_response = requests.get(transactions_url, headers=headers, params=params, cert=cert)
        transactions_response.raise_for_status()
        kb_transactions = transactions_response.json().get('transactions', [])
        print(f"--- DEBUG: Found {len(kb_transactions)} total transactions for IBAN {iban_to_sync}")
    except requests.RequestException as e:
        print(f"Warning: Could not fetch transactions for IBAN {iban_to_sync}: {e}")
        kb_transactions = []

    new_tx_count = 0
    for kb_tx in kb_transactions:
        tx_currency = kb_tx.get('amount', {}).get('currency')
        target_account = local_accounts_map.get(tx_currency)
        
        if not target_account:
            continue

        entry_ref = kb_tx.get('entryReference')
        booking_date = kb_tx.get('bookingDate', {}).get('date')
        value_date = kb_tx.get('valueDate', {}).get('date')
        amount = kb_tx.get('amount', {}).get('value')

        if not all([entry_ref, booking_date, value_date, amount is not None]):
            continue

        # Apply credit/debit logic
        if kb_tx.get('creditDebitIndicator') == 'DBIT':
            amount = -abs(amount)

        composite_tx_id = f"{entry_ref}-{booking_date}-{value_date}-{amount}-{tx_currency}"

        existing_tx = Transaction.query.filter_by(external_id=composite_tx_id, account_id=target_account.id).first()
        if not existing_tx:
            new_tx = Transaction(
                external_id=composite_tx_id,
                account_id=target_account.id,
                amount=amount,
                name=kb_tx.get('entryDetails', {}).get('transactionDetails', {}).get('relatedParties', {}).get('creditor', {}).get('name', 'Unknown'),
                date=datetime.strptime(booking_date.split('T')[0], '%Y-%m-%d').date(),
                description=kb_tx.get('entryDetails', {}).get('transactionDetails', {}).get('remittanceInformation', {}).get('unstructured', ''),
                currency=tx_currency,
                source='KB_API'
            )
            db.session.add(new_tx)
            new_tx_count += 1

    if new_tx_count > 0:
        print(f"--- DEBUG: Committing {new_tx_count} new transactions for IBAN {iban_to_sync}.")
        db.session.commit()

    for currency, account in local_accounts_map.items():
        session_id_for_balance = next((acc.get('id') for acc in accounts_by_iban[iban_to_sync] if acc.get('currency') == currency), None)
        if session_id_for_balance:
            balance_url = f"{base_url}/my/accounts/{session_id_for_balance}/balance"
            try:
                balance_response = requests.get(balance_url, headers=headers, cert=cert)
                balance_response.raise_for_status()
                balances = balance_response.json().get('balances', [])
                if balances:
                    account.balance = balances[0].get('amount', {}).get('value', account.balance)
            except requests.RequestException as e:
                print(f"Warning: Could not fetch balance for account {iban_to_sync} ({currency}): {e}")

    db.session.commit()
    
    return [acc.to_dict() for acc in local_accounts_map.values()]
