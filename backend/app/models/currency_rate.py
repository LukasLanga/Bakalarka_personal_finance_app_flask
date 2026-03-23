import datetime
from backend.app.db import db
from sqlalchemy.orm import relationship


class CurrencyRate(db.Model):
    __tablename__ = 'currency_rates'

    id = db.Column(db.Integer, primary_key=True)
    target_currency = db.Column(db.String(10), nullable=False)
    rate = db.Column(db.Numeric(10, 4), nullable=False)
    date = db.Column(db.Date, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('target_currency', 'date', name='uc_currency_rate_date'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'target_currency': self.target_currency,
            'rate': self.rate,
            'date': self.date
        }