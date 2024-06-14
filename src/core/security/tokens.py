import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError

from core.configuration import settings


def create_jwt_token(
    secret: str = settings.SECRET_KEY,
    expires_delta: timedelta | float = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    need_token_data: bool = False
) -> str:
    if not isinstance(expires_delta, timedelta):
        expires_delta = timedelta(minutes=expires_delta)
        
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "session": uuid.uuid4().hex,
    }
        
    encoded_jwt = jwt.encode(to_encode, secret, algorithm="HS256")

    if need_token_data:
        return encoded_jwt, to_encode
    
    return encoded_jwt


def verify_jwt_token(
    token: str,
    secret: str = settings.SECRET_KEY,
):    
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except:
        return None

    return payload