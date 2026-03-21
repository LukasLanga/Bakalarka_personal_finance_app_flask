from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from backend.app.db import db
from sqlalchemy.sql import func

class AccountRole(str, Enum):
    VIEWER = "viewer"
    EDITOR = "editor"
    MANAGER = "manager"
    OWNER = "owner"

class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"

class AccountInvitation(db.Model):
    __tablename__ = 'account_invitations'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    invited_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invited_email = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(50), nullable=False, default=InvitationStatus.PENDING.value)
    created_at = db.Column(db.DateTime, server_default=func.now())
    expires_at = db.Column(db.DateTime, nullable=False)

# Pydantic schema for API validation
class AccountInvitationSchema(BaseModel):
    id: int
    account_id: int
    invited_by_user_id: int
    invited_email: str
    role: AccountRole
    token: str
    status: InvitationStatus
    created_at: datetime
    expires_at: datetime

class CreateInvitation(BaseModel):
    invited_email: str
    role: AccountRole
