from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import jwt, JWTError
from .models import AdminUser, OTPStorage
import os
import uuid
import bcrypt
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/admin", tags=["Admin"])
otp_router = APIRouter(prefix="/admin/otp", tags=["OTP"])


SECRET_KEY = os.getenv("SECRET_KEY", "asdfgh")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")


class AdminCreateRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

class OTPVerifyRequest(BaseModel):
    email: str
    user_id: str
    otp: str

class OTPResendRequest(BaseModel):
    email: EmailStr
    user_id: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class PasswordResetRequest(BaseModel):
    email: EmailStr
    user_id: str
    password: str

# Response Models
class AdminCreateResponse(BaseModel):
    status: bool
    status_code: int
    description: str
    data: dict

class AdminLoginResponse(BaseModel):
    status: bool
    status_code: int
    description: str
    data: dict

class OTPVerifyResponse(BaseModel):
    status: bool
    status_code: int
    description: str
    data: list

class OTPResendResponse(BaseModel):
    status: bool
    status_code: int
    description: str
    data: dict

class ForgotPasswordResponse(BaseModel):
    status: bool
    status_code: int
    description: str
    data: list

class PasswordResetResponse(BaseModel):
    status: bool
    status_code: int
    description: str
    data: list


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def create_otp_record(email: str, user_id: str):
    OTPStorage.objects(email=email).delete()
    otp_code = "3812"  
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    OTPStorage(
        email=email,
        user_id=user_id,
        otp_code=otp_code,
        expires_at=expires_at
    ).save()
    print(f"OTP for {email}: {otp_code}")  
    return otp_code

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = AdminUser.objects(user_id=user_id).first()
    if user is None:
        raise credentials_exception
    return user

# Routes
@router.post("/create", response_model=AdminCreateResponse)
def create_admin_user(request: AdminCreateRequest):
    if AdminUser.objects(email=request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if AdminUser.objects(phone=request.phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")
    user_id = str(uuid.uuid4())
    roles = ["Admin", "Editor"]
    hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    access_token = create_access_token({"sub": user_id, "email": request.email, "roles": roles})
    admin = AdminUser(
        first_name=request.first_name,
        last_name=request.last_name,
        user_id=user_id,
        email=request.email,
        phone=request.phone,
        password=hashed_password,
        roles=roles,
        access_token=access_token
    )
    admin.save()
    return {
        "status": True,
        "status_code": 200,
        "description": "Admin account created",
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

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest):
    admin = AdminUser.objects(email=request.email).first()
    if not admin or not bcrypt.checkpw(request.password.encode('utf-8'), admin.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    await create_otp_record(email=request.email, user_id=admin.user_id)
    return {
        "status": True,
        "status_code": 200,
        "description": "We have sent you access code via mail verification",
        "data": {
            "email": admin.email,
            "user_id": admin.user_id
        }
    }

@otp_router.post("/verify", response_model=OTPVerifyResponse)
def verify_otp(request: OTPVerifyRequest):
    otp_record = OTPStorage.objects(email=request.email).first()
    if not otp_record or otp_record.otp_code != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if datetime.utcnow() > otp_record.expires_at:
        raise HTTPException(status_code=400, detail="OTP expired")
    admin = AdminUser.objects(email=request.email, user_id=request.user_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="User not found")
    access_token = create_access_token(
        {"sub": admin.user_id, "email": admin.email, "roles": admin.roles},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    admin.access_token = access_token
    admin.save()
    OTPStorage.objects(email=request.email).delete()
    user_data = {
        "first_name": admin.first_name,
        "last_name": admin.last_name,
        "user_name": f"{admin.first_name}{admin.last_name}",
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
        "access_token": access_token
    }
    return {
        "status": True,
        "status_code": 200,
        "description": "Admin signIn successful",
        "data": [user_data]
    }

@otp_router.post("/resend", response_model=OTPResendResponse)
async def resend_otp(request: OTPResendRequest):
    admin = AdminUser.objects(email=request.email, user_id=request.user_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="User not found")
    await create_otp_record(email=request.email, user_id=request.user_id)
    return {
        "status": True,
        "status_code": 200,
        "description": "We have sent you access code via mail verification",
        "data": {
            "email": admin.email,
            "user_id": admin.user_id
        }
    }

@router.post("/password/forgot", response_model=ForgotPasswordResponse)
async def forgot_password(request: ForgotPasswordRequest):
    admin = AdminUser.objects(email=request.email).first()
    if not admin:
        raise HTTPException(status_code=404, detail="User not found")
    await create_otp_record(email=request.email, user_id=admin.user_id)
    return {
        "status": True,
        "status_code": 200,
        "description": "We have sent you access code via mail verification",
        "data": [{"email": admin.email}]
    }

@router.post("/password/reset", response_model=PasswordResetResponse)
async def reset_password(request: PasswordResetRequest):
    
    admin = AdminUser.objects(email=request.email, user_id=request.user_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    
    hashed_password = bcrypt.hashpw(
        request.password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    admin.password = hashed_password
    admin.updated_at = datetime.utcnow()
    admin.save()

    return {
        "status": True,
        "status_code": status.HTTP_200_OK,
        "description": "Password updated successfully",
        "data": [{
            "user_id": admin.user_id,
            "email": admin.email
        }]
    }



router.include_router(otp_router)
