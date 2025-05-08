from mongoengine import Document, StringField, BooleanField, DateTimeField, ListField
from datetime import datetime

class AdminUser(Document):
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    user_id = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    phone = StringField(required=True)
    password = StringField(required=True)
    status = BooleanField(default=True)
    roles = ListField(StringField(), default=["Admin"])
    created_at = DateTimeField(default=datetime.utcnow)
    created_by = StringField(default="")
    updated_at = DateTimeField(default=datetime.utcnow)
    updated_by = StringField(default="")
    profile_image = StringField(default="")
    verification_status = BooleanField(default=False)
    access_token = StringField(default="")
