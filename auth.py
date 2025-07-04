from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from config import settings
import schemas
import crud
from database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# 2025/06/29 16:02
token_blacklist = set()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# 2025/06/29 16:02
def is_token_blacklisted(token: str):
    return token in token_blacklist

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 2025/06/29 16:02
    if is_token_blacklisted(token):
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    db = SessionLocal()
    user = crud.get_user_by_username(db, username=token_data.username)
    db.close()
    
    if user is None:
        raise credentials_exception
    return user