from datetime import datetime, timedelta
import os
import bcrypt
from jose import jwt
from models import OTPStorage
from dotenv import load_dotenv

# Initialize environment variables
load_dotenv()  # Now properly called

# Configuration
ACCESS_TOKEN_EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
OTP_EXPIRE = int(os.getenv("OTP_EXPIRE_MINUTES"))

# Import SECRET_KEY from auth (circular import fix)
try:
    from auth import SECRET_KEY
except ImportError:
    SECRET_KEY = os.getenv("SECRET_KEY") or "fallback-secret-for-dev-only"  # Remove in production

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_access_token(data: dict) -> str:
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    data.update({"exp": expires})
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")

async def create_otp_record(email: str, user_id: str) -> str:
    OTPStorage.objects(email=email).delete()
    otp = "3812"  # Generate proper OTP in production
    expires = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE)
    OTPStorage(
        email=email,
        user_id=user_id,
        otp_code=otp,
        expires_at=expires
    ).save()
    print(f"OTP for {email}: {otp}")
    return otp
