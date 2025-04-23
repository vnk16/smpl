from jose import JWTError, jwt
from fastapi import Depends
from models import AdminUser
from utils import verify_password
import os

# Define SECRET_KEY here (temporary solution)
SECRET_KEY = os.getenv("SECRET_KEY") or "your-super-secret-key-here"  # MUST change in production

async def authenticate_user(email: str, password: str):
    admin = AdminUser.objects(email=email).first()
    if not admin or not verify_password(password, admin.password):
        return None
    return admin

async def get_current_user(token: str):
    credentials_exception = {
        "status": False,
        "error": "Invalid credentials",
        "status_code": 401
    }
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = AdminUser.objects(user_id=user_id).first()
    if user is None:
        raise credentials_exception
    return user
