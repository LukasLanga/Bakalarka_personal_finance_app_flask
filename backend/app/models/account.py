from backend.app.db import db
from sqlalchemy.orm import relationship

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bank_name = db.Column(db.String(100), nullable=True)
    balance = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(10), nullable=False, default='EUR')

    accesses = relationship(
        "UserAccountAccess",
        back_populates="account",
        cascade="all, delete-orphan"
    )

    psd2_connection = relationship(
        "Psd2Connection",
        back_populates="account",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'bank_name': self.bank_name,
            'balance': float(self.balance),
            'currency': self.currency
        }

    def __repr__(self):
        return f'<Account {self.name} (ID: {self.id}, Balance: {self.balance} {self.currency})>'
