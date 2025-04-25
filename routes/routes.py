# routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime
from mongoengine.errors import NotUniqueError
from models.models import AdminUser
from utils import generate_access_token, generate_uuid
import uuid

router = APIRouter(prefix="/admin", tags=["Admin"])

class AdminCreateRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str

class AdminCreateResponse(BaseModel):
    status: bool
    status_code: int
    description: str
    data: dict

@router.post("/create", response_model=AdminCreateResponse)
def create_admin_user(request: AdminCreateRequest):
    # Check if user already exists
    if AdminUser.objects(email=request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if AdminUser.objects(phone=request.phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")

    user_id = generate_uuid()
    roles = ["Admin", "Editor"]
    now = datetime.utcnow()
    access_token = generate_access_token({"sub": user_id, "email": request.email, "roles": roles})

    try:
        admin = AdminUser(
            first_name=request.first_name,
            last_name=request.last_name,
            user_id=user_id,
            email=request.email,
            phone=request.phone,
            password=request.password,  # Hash in production!
            status=True,
            roles=roles,
            created_at=now,
            created_by="",
            updated_at=now,
            updated_by="",
            profile_image="",
            verification_status=True,
            access_token=access_token
        )
        admin.save()
    except NotUniqueError:
        raise HTTPException(status_code=400, detail="User already exists")

    return {
        "status": True,
        "status_code": 200,
        "description": "admin account created",
        "data": {
            "first_name": admin.first_name,
            "last_name": admin.last_name,
            "user_id": admin.user_id,
            "email": admin.email,
            "phone": admin.phone,
            "status": admin.status,
            "roles": admin.roles,
            "created_at": admin.created_at.isoformat() + "Z",
            "created_by": admin.created_by,
            "updated_at": admin.updated_at.isoformat() + "Z",
            "updated_by": admin.updated_by,
            "profile_image": admin.profile_image,
            "verification_status": admin.verification_status,
            "access_token": admin.access_token
        }
    }

class AdminAccountApprovalRequest(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    verification_status: bool  # True: Approved, False: Rejected
    email_note: str
    approved_by: str  # Admin who approves the account

class AdminAccountApprovalResponse(BaseModel):
    status: bool
    status_code: int
    description: str
    data: list

@router.post("/account/approval", response_model=AdminAccountApprovalResponse)
def approve_admin_account(request: AdminAccountApprovalRequest):
    # Find the user by user_id
    admin_user = AdminUser.objects(user_id=request.user_id).first()

    if not admin_user:
        raise HTTPException(status_code=404, detail="Admin user not found")

    # Update the verification status and approval details
    admin_user.verification_status = request.verification_status
    admin_user.updated_at = datetime.utcnow()
    admin_user.updated_by = request.approved_by

    # You can add logic here to send the approval/rejection email (for example using an SMTP service)

    # Save the changes
    admin_user.save()

    # Return a success response
    return {
        "status": True,
        "status_code": 200,
        "description": "Admin account approval updated successfully",
        "data": [{
            "first_name": admin_user.first_name,
            "last_name": admin_user.last_name,
            "user_id": admin_user.user_id,
            "email": admin_user.email,
            "phone": admin_user.phone,
            "status": admin_user.status,
            "roles": admin_user.roles,
            "created_at": admin_user.created_at.isoformat() + "Z",
            "created_by": admin_user.created_by,
            "updated_at": admin_user.updated_at.isoformat() + "Z",
            "updated_by": admin_user.updated_by,
            "profile_image": admin_user.profile_image,
            "verification_status": admin_user.verification_status
        }]
    }