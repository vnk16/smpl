from mongoengine import connect
from dotenv import load_dotenv
import os

load_dotenv()

def connect_db():
    connect(
        db=os.getenv("DB_NAME"),
        host=os.getenv("MONGO_URI"),
        alias="default"
    )
