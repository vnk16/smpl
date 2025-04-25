# utils.py
import uuid
from datetime import datetime, timedelta
from jose import jwt
from auth.auth import SECRET_KEY, ALGORITHM

# Function to generate a JWT access token
def generate_access_token(data: dict, expires_delta: timedelta = timedelta(hours=2)) -> str:
    """
    Generate a JWT token with expiration time.
    
    :param data: The payload data to include in the token (typically a user id or roles).
    :param expires_delta: The expiration duration for the token (default is 2 hours).
    :return: The encoded JWT token as a string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to generate a random unique identifier (UUID)
def generate_uuid() -> str:
    """
    Generate a random unique identifier (UUID).
    
    :return: A unique UUID string.
    """
    return str(uuid.uuid4())
