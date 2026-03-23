from backend.app.db import db
from backend.app.models import Transaction, UserAccountAccess, Account, Category
from backend.app.models.user import User
from backend.app.services.account_service import AccountService
from backend.app.services.category_service import CategoryService
from sqlalchemy import func, extract, or_
from datetime import datetime
from decimal import Decimal

class TransactionService:

    @staticmethod
    def get_recent_transactions(user: User, limit: int = 5, account_id: int = None):
        if account_id:
            access = UserAccountAccess.query.filter_by(user_id=user.id, account_id=account_id).first()
            if not access:
                return []
            account_ids = [account_id]
        else:
            account_ids = [acc.id for acc in AccountService.list_accounts(user)]
        
        if not account_ids:
            return []

        return db.session.query(Transaction).filter(
            Transaction.account_id.in_(account_ids)
        ).order_by(Transaction.date.desc(), Transaction.id.desc()).limit(limit).all()

    @staticmethod
    def get_transactions_between_dates(user: User, start_date: datetime, end_date: datetime, account_id: int = None):
        if account_id:
            access = UserAccountAccess.query.filter_by(user_id=user.id, account_id=account_id).first()
            if not access:
                return []
            account_ids = [account_id]
        else:
            account_ids = [acc.id for acc in AccountService.list_accounts(user)]
        
        if not account_ids:
            return []

        return db.session.query(Transaction).filter(
            Transaction.account_id.in_(account_ids),
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()

    @staticmethod
    def get_dashboard_summary(user: User, year: int, month: int, recent_transaction_limit: int = 5, account_id: int = None):
        if account_id:
            access = UserAccountAccess.query.filter_by(user_id=user.id, account_id=account_id).first()
            if not access:
                 return {
                    "total_balance": 0,
                    "monthly_income": 0,
                    "monthly_expenses": 0,
                    "recent_transactions": [],
                    "spending_by_category": [],
                }
            account_ids = [account_id]
            total_balance = AccountService.get_account_balance(user, account_id)
        else:
            user_accounts = AccountService.list_accounts(user)
            if not user_accounts:
                return {
                    "total_balance": 0,
                    "monthly_income": 0,
                    "monthly_expenses": 0,
                    "recent_transactions": [],
                    "spending_by_category": [],
                }
            account_ids = [acc.id for acc in user_accounts]
            total_balance = AccountService.get_total_balance(user)

        monthly_transactions_query = db.session.query(Transaction).filter(
            Transaction.account_id.in_(account_ids),
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        )

        monthly_income = monthly_transactions_query.filter(Transaction.amount > 0).with_entities(func.sum(Transaction.amount)).scalar() or 0
        monthly_expenses = monthly_transactions_query.filter(Transaction.amount < 0).with_entities(func.sum(Transaction.amount)).scalar() or 0

        recent_transactions = TransactionService.get_recent_transactions(user, limit=recent_transaction_limit, account_id=account_id)

        spending_by_category = db.session.query(
            Category.name,
            func.sum(Transaction.amount).label('total_spent')
        ).join(Transaction, Transaction.category_id == Category.id).filter(
            Transaction.account_id.in_(account_ids),
            Transaction.amount < 0,
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).group_by(Category.name).order_by(func.sum(Transaction.amount).asc()).all()

        return {
            "total_balance": total_balance,
            "monthly_income": monthly_income,
            "monthly_expenses": abs(monthly_expenses),
            "recent_transactions": [t.to_dict() for t in recent_transactions],
            "spending_by_category": [{"category_name": name, "amount": abs(total)} for name, total in spending_by_category],
        }

    @staticmethod
    def create_transaction(user: User, account_id: int, amount: Decimal, name: str, description: str = None, category_id: int = None, date: datetime = None, currency: str = 'EUR'):
        access = UserAccountAccess.query.filter_by(user_id=user.id, account_id=account_id).first()
        if not access:
            raise PermissionError('User does not have access to this account.')

        account = Account.query.get(account_id)
        if not account:
            raise ValueError("Account not found.")

        if category_id:
            if not CategoryService.user_category_exists(user, category_id):
                raise ValueError("Category not found or does not belong to user.")

        transaction = Transaction(
            account_id=account_id,
            category_id=category_id,
            name=name,
            amount=amount,
            date=date,
            description=description,
            currency=currency,
            source='manual',
            external_id=None
        )

        account.balance += amount
        db.session.add(transaction)
        db.session.commit()
        return transaction

    @staticmethod
    def update_transaction(user: User, transaction_id: int, account_id: int, amount: Decimal = None, name: str = None, description: str = None, category_id: int = None, date: datetime = None):
        access = UserAccountAccess.query.filter_by(user_id=user.id, account_id=account_id).first()
        if not access:
            raise PermissionError('User does not have access to this account')
        
        transaction = Transaction.query.get(transaction_id)
        if not transaction or transaction.account_id != account_id:
            raise ValueError('Transaction not found')

        account = Account.query.get(account_id)
        
        if amount is not None:
            account.balance -= transaction.amount
            transaction.amount = amount
            account.balance += amount
        
        if name is not None:
            transaction.name = name
        if description is not None:
            transaction.description = description
        if date is not None:
            transaction.date = date
        if category_id is not None:
             if not CategoryService.user_category_exists(user, category_id):
                raise ValueError("Category not found or does not belong to user.")
             transaction.category_id = category_id

        db.session.commit()
        return transaction

    @staticmethod
    def delete_transaction(user: User, account_id, transaction_id):
        access = UserAccountAccess.query.filter_by(user_id=user.id, account_id=account_id).first()
        if not access:
            raise PermissionError('User does not have access to this account')
        transaction = Transaction.query.get(transaction_id)
        if not transaction or transaction.account_id != account_id:
            raise ValueError('Transaction not found')

        account = Account.query.get(transaction.account_id)
        account.balance -= transaction.amount

        db.session.delete(transaction)
        db.session.commit()

    @staticmethod
    def get_transaction(user: User, account_id, transaction_id):
        access = UserAccountAccess.query.filter_by(user_id=user.id, account_id=account_id).first()
        if not access:
            raise PermissionError('User does not have access to this account')
        transaction = Transaction.query.get(transaction_id)
        if not transaction or transaction.account_id != account_id:
            raise ValueError('Transaction not found')
        return transaction

    @staticmethod
    def get_all_transactions(user: User, page: int = 1, per_page: int = 10, search_query: str = None, account_id: int = None, category_id: int = None):
        account_ids = [acc.id for acc in AccountService.list_accounts(user)]
        if not account_ids:
            return []
        
        query = Transaction.query.filter(Transaction.account_id.in_(account_ids))

        if search_query:
            query = query.filter(or_(
                Transaction.name.ilike(f"%{search_query}%"),
                Transaction.description.ilike(f"%{search_query}%")
            ))
        
        if account_id:
            query = query.filter(Transaction.account_id == account_id)

        if category_id:
            query = query.filter(Transaction.category_id == category_id)

        return query.order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_all_transactions_by_category(user: User, category_id):
        if not CategoryService.user_category_exists(user, category_id):
            raise ValueError("Category not found or does not belong to user.")
        
        account_ids = [acc.id for acc in AccountService.list_accounts(user)]
        return Transaction.query.filter(
            Transaction.account_id.in_(account_ids),
            Transaction.category_id == category_id
        ).all()

    @staticmethod
    def get_all_transactions_by_account(user: User, account_id):
        access = UserAccountAccess.query.filter_by(user_id=user.id, account_id=account_id).first()
        if not access:
            raise PermissionError('User does not have access to this account')
        return Transaction.query.filter_by(account_id=account_id).all()
