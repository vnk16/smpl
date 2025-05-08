from mongoengine import connect
import os
from dotenv import load_dotenv

load_dotenv()

def connect_to_mongo():
    connect(
        db=os.getenv("MONGO_DB"),
        host=os.getenv("MONGO_URI")
    )
