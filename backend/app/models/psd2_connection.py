from backend.app.db import db
from sqlalchemy.orm import relationship

class Psd2Connection(db.Model):
    __tablename__ = 'psd2_connection'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), unique=True, nullable=True)
    bank_name = db.Column(db.String(100), nullable=False)
    client_id = db.Column(db.String(255), unique=True, nullable=True)
    access_token = db.Column(db.Text, nullable=True)
    refresh_token = db.Column(db.Text, nullable=True)
    token_expires_at = db.Column(db.TIMESTAMP, nullable=True)
    last_synced = db.Column(db.TIMESTAMP, server_default=db.func.now(), onupdate=db.func.now())

    user = relationship("User", back_populates="psd2_connections")
    account = relationship("Account")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_id': self.account_id,
            'bank_name': self.bank_name,
            'client_id': self.client_id,
            'last_synced': self.last_synced.isoformat() if self.last_synced else None
        }
