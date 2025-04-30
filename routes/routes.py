from fastapi import APIRouter,Body
from models.models import AdminUser
from utils import hash_password
from auth.generate_token import create_access_token, verify_token
import datetime
import uuid
import bcrypt
from jose import jwt, JWTError



router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/create")
async def create_admin(
    first_name: str=Body(...),
    last_name: str=Body(...),
    email: str=Body(...),
    phone: str=Body(...),
    password: str=Body(...)
):
    try:
        if AdminUser.objects(email=email).first():
            return {
                "status": False,
                "status_code": 400,
                "description": "Admin with this email already exists",
                "data": []
            }

        user_id = str(uuid.uuid4())
        hashed_pw = hash_password(password)
        token = create_access_token({"sub": user_id, "email": email, "roles": ["Admin", "Editor"]})

        admin = AdminUser(
            first_name=first_name,
            last_name=last_name,
            user_id=user_id,
            email=email,
            phone=phone,
            password=hashed_pw,
            roles=["Admin", "Editor"],
            access_token=token
        )
        admin.save()

        Users = {
            "first_name": admin.first_name,
            "last_name": admin.last_name,
            "user_id": admin.user_id,
            "email": admin.email,
            "phone": admin.phone,
            "status": admin.status,
            "roles": admin.roles,
            "created_at": admin.created_at.isoformat(),
            "created_by": admin.created_by,
            "updated_at": admin.updated_at.isoformat(),
            "updated_by": admin.updated_by,
            "profile_image": admin.profile_image,
            "verification_status": admin.verification_status,
            "access_token": admin.access_token
        }
        return {
            "status": True,
            "status_code": 201,
            "description": "admin account created",
            "data": [Users]
        }

    except Exception as e:
        return {
            "status": False,
            "status_code": 500,
            "description": f"Internal Server Error: {str(e)}",
            "data": []
        }

@router.post("/account/approval")
async def approve_admin_account(
    user_id: str=Body(...),
    first_name: str=Body(...),
    last_name: str=Body(...),
    email: str=Body(...),
    phone: str=Body(...),
    verification_status: bool=Body(...),
    email_note: str=Body("Dear user, your account creation request has been approved, you may receive your password via system generated email. Please check and proceed with login to Zukarte Admin Portal. Thank You!"),
    approved_by: str=Body(...),
    token: str=Body  # Passed in body
):
    token_data = verify_token(token)
    if not token_data:
        return {
            "status": False,
            "status_code": 401,
            "description": "Invalid or expired token",
            "data": []
        }

    try:
        admin = AdminUser.objects(user_id=user_id).first()
        if not admin:
            return {
                "status": False,
                "status_code": 404,
                "description": "Admin user not found",
                "data": []
            }

        admin.update(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            verification_status=verification_status,
            updated_at=datetime.datetime.utcnow(),
            updated_by=approved_by
        )

        updated_admin = AdminUser.objects(user_id=user_id).first()
        Users = {
            "first_name": updated_admin.first_name,
            "last_name": updated_admin.last_name,
            "user_id": updated_admin.user_id,
            "email": updated_admin.email,
            "phone": updated_admin.phone,
            "status": updated_admin.status,
            "roles": updated_admin.roles,
            "created_at": updated_admin.created_at.isoformat(),
            "created_by": updated_admin.created_by,
            "updated_at": updated_admin.updated_at.isoformat(),
            "updated_by": updated_admin.updated_by,
            "profile_image": updated_admin.profile_image,
            "verification_status": updated_admin.verification_status
        }

        return {
            "status": True,
            "status_code": 200,
            "description": "admin account approved",
            "data": [Users]
        }

    except Exception as e:
        return {
            "status": False,
            "status_code": 500,
            "description": f"Internal Server Error: {str(e)}",
            "data": []
        }

@router.post("/login")
async def admin_login(
    email: str=Body(...),
    password: str=Body(...), 
    token: str=Body
    
    ):
    token_data = verify_token(token)
    if not token_data:
        return {
            "status": False,
            "status_code": 401,
            "description": "Invalid or expired token",
            "data": []
        }
    admin = AdminUser.objects(email=email).first()
    if not admin or not bcrypt.checkpw(password.encode(), admin.password.encode()):
        return {
            "status": False,
            "status_code": 401,
            "description": "Invalid credentials",
            "data": []
        }
    
    return {
        "status": True,
        "status_code": 200,
        "description": "We have sent you access code via mail verification",
        "data": {
            "email": email,
            "user_id": admin.user_id
        }
    }

@router.post("/otp/verify")
async def verify_otp(
    email: str=Body(...), 
    user_id: str=Body(...), 
    otp: str=Body(...), 
    token: str=Body
    ):
    token_data = verify_token(token)
    if not token_data:
        return {
            "status": False,
            "status_code": 401,
            "description": "Invalid or expired token",
            "data": []
        }
    admin = AdminUser.objects(email=email, user_id=user_id).first()
    if not admin:
        return {
            "status": False,
            "status_code": 404,
            "description": "Admin not found",
            "data": []
        }

    if otp != "3812":  # Example only. Replace with real OTP validation logic
        return {
            "status": False,
            "status_code": 400,
            "description": "Invalid OTP or account not verified",
            "data": []
        }
    adminData={
            "first_name": admin.first_name,
            "last_name": admin.last_name,
            "user_name": admin.first_name + admin.last_name,
            "user_id": admin.user_id,
            "email": admin.email,
            "phone": admin.phone,
            "status": admin.status,
            "roles": admin.roles,
            "created_at": admin.created_at.isoformat(),
            "created_by": admin.created_by,
            "updated_at": admin.updated_at.isoformat(),
            "updated_by": admin.updated_by,
            "profile_image": admin.profile_image,
            "verification_status": admin.verification_status,
            "access_token": admin.access_token
        }

    return {
        "status": True,
        "status_code": 200,
        "description": "Admin signIn successful",
        "data": [adminData]
    }

