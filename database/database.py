# database.py
from mongoengine import connect

def connect_db():
    connect(db="act", host="mongodb://localhost:27017/act")
