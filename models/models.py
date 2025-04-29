from mongoengine import Document, StringField, BooleanField, ListField, DateTimeField
import datetime

class AdminUser(Document):
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    user_id = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    phone = StringField(required=True)
    password = StringField(required=True)
    status = BooleanField(default=True)
    roles = ListField(StringField(), default=["Admin"])
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    created_by = StringField()
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_by = StringField()
    profile_image = StringField()
    verification_status = BooleanField(default=False)
    access_token = StringField()
