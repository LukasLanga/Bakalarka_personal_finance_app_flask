from pydantic import BaseModel
from datetime import datetime
from enum import Enum

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

class AccountInvitation(BaseModel):
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
