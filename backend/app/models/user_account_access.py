from backend.app.db import db
from sqlalchemy.orm import relationship


class UserAccountAccess(db.Model):
    __tablename__ = 'user_account_access'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    role = db.Column(db.String(50), nullable=False, default='owner')

    user = relationship("User", back_populates="account_accesses")
    account = relationship("Account", back_populates="accesses")

    def __repr__(self):
        return f'<UserAccountAccess User {self.user_id} -> Account {self.account_id} (Role: {self.role})>'
