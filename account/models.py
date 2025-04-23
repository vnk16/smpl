from mongoengine import Document, StringField, BooleanField, ListField, DateTimeField
from datetime import datetime

class AdminUser(Document):
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    user_id = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    phone = StringField(required=True, unique=True)
    password = StringField(required=True)  
    status = BooleanField(default=True)
    roles = ListField(StringField(), default=list)
    created_at = DateTimeField(default=datetime.utcnow)
    created_by = StringField()
    updated_at = DateTimeField(default=datetime.utcnow)
    updated_by = StringField()
    profile_image = StringField()
    verification_status = BooleanField(default=False)
    access_token = StringField()

class OTPStorage(Document):
    email = StringField(required=True, unique=True)
    user_id = StringField(required=True)
    otp_code = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()
