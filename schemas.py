from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class AdminApprovalRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    first_name: str = Field("", max_length=50)
    last_name: str = Field("", max_length=50)
    email: str = Field("", max_length=100)
    phone: str = Field("", max_length=20)
    verification_status: bool
    email_note: str = Field(
        default="Dear user, your account creation request has been approved...",
        min_length=1
    )
    approved_by: str = Field(..., min_length=1)

class AdminUserData(BaseModel):
    first_name: str
    last_name: str
    user_id: str
    email: str
    phone: str
    status: bool
    roles: List[str]
    created_at: str
    created_by: str
    updated_at: str
    updated_by: str
    profile_image: str
    verification_status: bool
    email_note: str

class AdminApprovalResponse(BaseModel):
    status: bool
    status_code: int
    description: str
    data: List[AdminUserData]
