from backend.app.db import db
from sqlalchemy.orm import relationship

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    amount = db.Column(db.Numeric(12, 2), nullable=True)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    source = db.Column(db.String(20), nullable=False)
    external_id = db.Column(db.String(100), nullable=True)





    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'category_id': self.category_id,
            'amount': self.amount,
            'date': self.date,
            'description': self.description,
            'currency': self.currency,
            'source': self.source,
            'external_id': self.external_id
        }