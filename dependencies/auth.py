import jwt
import datetime
from app.config.settings import settings

def create_access_token(data: dict):
    to_encode = data.copy()

    # Set expiration time for the token
    expires_delta = datetime.timedelta(minutes=int(settings.TOKEN_EXPIRATION))
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token