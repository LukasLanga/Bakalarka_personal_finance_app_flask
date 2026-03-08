from backend.app.db import db
from backend.app.models import User, Account, UserAccountAccess
from sqlalchemy import func

class AccountService:

    @staticmethod
    def get_total_balance(user: User) -> float:
        """Calculates the sum of balances across all users accounts."""
        account_ids = [acc.id for acc in AccountService.list_accounts(user)]
        if not account_ids:
            return 0.0
        
        total_balance = db.session.query(func.sum(Account.balance)).filter(Account.id.in_(account_ids)).scalar()
        return total_balance or 0.0

    @staticmethod
    def create_account(user: User, name: str, balance: float, bank_name: str, currency: str) -> Account:
        new_account = Account(name=name, balance=balance, bank_name=bank_name, currency=currency)
        new_access = UserAccountAccess(user=user, account=new_account, role="owner")

        db.session.add(new_account)
        db.session.add(new_access)
        db.session.commit()

        return new_account

    @staticmethod
    def update_account(user: User, account_id: int, name: str = None, bank_name: str = None, currency: str = None) -> Account:
        access = UserAccountAccess.query.filter_by(user_id=user.id, account_id=account_id).first()
        if not access or access.role != 'owner':
            raise PermissionError("No permission to update this account")

        account = Account.query.get(account_id)
        if not account:
            raise ValueError("Account not found")

        if name:
            account.name = name
        if bank_name:
            account.bank_name = bank_name
        if currency:
            account.currency = currency
        
        db.session.commit()
        return account

    @staticmethod
    def delete_account(user: User, account_id: int):
        access =  UserAccountAccess.query.filter_by(user_id=user.id, account_id=account_id).first()
        if not access:
            return False

        if access.role == 'owner':
            from backend.app.models import Transaction
            Transaction.query.filter_by(account_id=account_id).delete()
            UserAccountAccess.query.filter_by(account_id=account_id).delete()

            account = Account.query.get(account_id)
            db.session.delete(account)
            db.session.commit()
            return True
        return False

    @staticmethod
    def add_user(user: User, account_id: int, email: str, role: str):
        access =  UserAccountAccess.query.filter_by(user_id=user.id, account_id=account_id).first()
        if not access or access.role != 'owner':
            raise PermissionError("No permission to add users to this account")

        account = Account.query.get(account_id)
        user_to_add = User.query.filter_by(email=email).first()

        if not account or not user_to_add:
            raise ValueError("Account or user to add not found.")

        # Check if user already has access
        if UserAccountAccess.query.filter_by(user_id=user_to_add.id, account_id=account.id).first():
            raise ValueError("User already has access to this account.")

        new_access = UserAccountAccess(user=user_to_add, account=account, role=role)
        db.session.add(new_access)
        db.session.commit()
        return True

    @staticmethod
    def remove_user(user: User, account_id: int, email: str):
        access = UserAccountAccess.query.filter_by(user_id=user.id, account_id=account_id).first()

        if not access or access.role != 'owner':
            raise PermissionError("No permission to remove users from this account")

        user_to_remove = User.query.filter_by(email=email).first()
        if not user_to_remove:
            raise ValueError("User to remove not found.")
        
        if user_to_remove.id == user.id:
            raise ValueError("Cannot remove yourself from an account.")

        access_to_delete = UserAccountAccess.query.filter_by(user_id=user_to_remove.id, account_id=account_id).first()
        if not access_to_delete:
            raise ValueError("User does not have access to this account.")

        db.session.delete(access_to_delete)
        db.session.commit()
        return True

    @staticmethod
    def list_users(user: User, account_id: int):
        if not UserAccountAccess.query.filter_by(user_id=user.id, account_id=account_id).first():
            raise PermissionError("No permission to list users of this account")

        all_accesses = UserAccountAccess.query.filter_by(account_id=account_id).all()
        return [access.user for access in all_accesses]

    @staticmethod
    def get_account_balance(user: User, account_id: int):
        if not UserAccountAccess.query.filter_by(user_id=user.id, account_id=account_id).first():
            raise PermissionError("No permission to get balance from this account")

        account = Account.query.get(account_id)
        return account.balance

    @staticmethod
    def list_accounts(user: User):
        accounts = Account.query.join(
            UserAccountAccess).filter(
            UserAccountAccess.user_id == user.id
        ).all()
        return accounts

    @staticmethod
    def user_account_exists(user: User, account_id: int):
        return UserAccountAccess.query.filter_by(user_id=user.id, account_id=account_id).first() is not None
