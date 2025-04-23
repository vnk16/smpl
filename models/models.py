from mongoengine import Document, StringField, DateTimeField, BooleanField, ListField
from datetime import datetime

class AdminUser(Document):
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    user_id = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    phone = StringField(required=True, unique=True)
    password = StringField(required=True)
    status = BooleanField(default=True)
    roles = ListField(StringField(), default=["Admin"])
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    access_token = StringField()
    verification_status = BooleanField(default=False)

class OTPStorage(Document):
    email = StringField(required=True, unique=True)
    user_id = StringField(required=True)
    otp_code = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(required=True)
