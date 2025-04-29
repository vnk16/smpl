from fastapi import APIRouter,Body
from models.models import AdminUser
from utils import generate_user_id, hash_password
from auth.generate_token import create_access_token
import datetime

router = APIRouter()

@router.post("/admin/create")
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
                "description": "Email already exists",
                "data": []
            }

        user_id = generate_user_id()
        hashed_pw = hash_password(password)
        token = create_access_token({"sub": user_id, "email": email, "roles": ["Admin"]})

        admin = AdminUser(
            first_name=first_name,
            last_name=last_name,
            user_id=user_id,
            email=email,
            phone=phone,
            password=hashed_pw,
            status=True,
            roles=["Admin", "Editor"],
            created_by="",
            updated_by="",
            profile_image="",
            verification_status=True,
            access_token=token,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
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
            "status_code": 200,
            "description": "user created successfully",
            "data": [Users]
        }

    except Exception as e:
        return {
            "status": False,
            "status_code": 500,
            "description": f"Internal Server Error: {str(e)}",
            "data": []
        }
