from datetime import datetime, timedelta
import os
import uuid
import bcrypt
from jose import jwt, JWTError
from fastapi import APIRouter
from account.models.models import AdminUser, OTPStorage
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(prefix="/admin", tags=["Admin"])
otp_router = APIRouter(prefix="/admin/otp", tags=["OTP"])

# Config
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
OTP_EXPIRE = int(os.getenv("OTP_EXPIRE_MINUTES"))

# Utility Functions
def create_access_token(data: dict):
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    data.update({"exp": expires})
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")

async def create_otp_record(email: str, user_id: str):
    OTPStorage.objects(email=email).delete()
    otp = "3812"  # Generate proper OTP in production
    expires = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE)
    OTPStorage(
        email=email,
        user_id=user_id,
        otp_code=otp,
        expires_at=expires
    ).save()
    print(f"OTP for {email}: {otp}")  # Remove in production
    return otp

# Auth Endpoints
@router.post("/create")
async def create_admin(
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    password: str
):
    if AdminUser.objects(email=email).first():
        return {"status": False, "error": "Email exists", "status_code": 400}

    user_id = str(uuid.uuid4())
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    token = create_access_token({"sub": user_id, "email": email, "roles": ["Admin"]})
    
    admin = AdminUser(
        first_name=first_name,
        last_name=last_name,
        user_id=user_id,
        email=email,
        phone=phone,
        password=hashed_pw,
        access_token=token
    ).save()

    return {
        "status": True,
        "status_code": 201,
        "data": {
            "user_id": user_id,
            "email": email,
            "access_token": token
        }
    }

@router.post("/login")
async def admin_login(email: str, password: str):
    admin = AdminUser.objects(email=email).first()
    if not admin or not bcrypt.checkpw(password.encode(), admin.password.encode()):
        return {"status": False, "error": "Invalid credentials", "status_code": 401}

    await create_otp_record(email, admin.user_id)
    return {
        "status": True,
        "status_code": 200,
        "data": {"email": email, "user_id": admin.user_id}
    }

@otp_router.post("/verify")
async def verify_otp(email: str, user_id: str, otp: str):
    record = OTPStorage.objects(email=email).first()
    if not record or record.otp_code != otp:
        return {"status": False, "error": "Invalid OTP", "status_code": 400}
    
    if datetime.utcnow() > record.expires_at:
        return {"status": False, "error": "OTP expired", "status_code": 400}

    admin = AdminUser.objects(email=email, user_id=user_id).first()
    if not admin:
        return {"status": False, "error": "User not found", "status_code": 404}

    token = create_access_token({"sub": user_id, "email": email, "roles": admin.roles})
    admin.update(access_token=token, verification_status=True)
    record.delete()

    return {
        "status": True,
        "status_code": 200,
        "data": {
            "access_token": token,
            "user_id": user_id,
            "email": email
        }
    }

@otp_router.post("/resend")
async def resend_otp(email: str, user_id: str):
    admin = AdminUser.objects(email=email, user_id=user_id).first()
    if not admin:
        return {"status": False, "error": "User not found", "status_code": 404}

    await create_otp_record(email, user_id)
    return {"status": True, "status_code": 200, "data": {"email": email}}

@router.post("/password/forgot")
async def forgot_password(email: str):
    admin = AdminUser.objects(email=email).first()
    if not admin:
        return {"status": False, "error": "User not found", "status_code": 404}

    await create_otp_record(email, admin.user_id)
    return {"status": True, "status_code": 200, "data": {"email": email}}

@router.post("/password/reset")
async def reset_password(email: str, user_id: str, password: str):
    admin = AdminUser.objects(email=email, user_id=user_id).first()
    if not admin:
        return {"status": False, "error": "User not found", "status_code": 404}

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    admin.update(password=hashed_pw, updated_at=datetime.utcnow())
    
    return {
        "status": True,
        "status_code": 200,
        "data": {"email": email, "user_id": user_id}
    }

router.include_router(otp_router)
