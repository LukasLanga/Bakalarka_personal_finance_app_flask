from backend.app.db import db
from sqlalchemy.orm import relationship

class PSD2Connection(db.Model):
    __tablename__ = 'psd2_connection'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    bank_name = db.Column(db.String(100), nullable=False)
    client_id = db.Column(db.String(255), nullable=False)
    access_token = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.String(255), nullable=False)
    token_expires_at = db.Column(db.Timestamp, nullable=True)
    last_synced = db.Column(db.Timestamp, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_id': self.account_id,
            'bank_name': self.bank_name,
            'client_id': self.client_id
        }