from fastapi import Depends, HTTPException, status
from fastapi.security import  OAuth2PasswordBearer
from jose import jwt,JWTError
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from app import schema, database, models
from app.database  import get_db
oath2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
# SECRET KEY
SECRET_KEY = "0d690e0500ca3761119ad0300a4a964a988078648b13001cdb735387208a0b3a84983847"

# algorithm
ALGORITHM = "HS256"

# token Expiration time
ACCESS_TOKEN_EXPIRE_MIN = 60

def create_access_token(data: dict):
    to_encode = data.copy()

    # provide the time it's going to expire in i.e countdown from now
    expire = datetime.now() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MIN)
    to_encode.update({"exp": expire})

    # this method will create the jwt token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

        id: str = payload.get("id")
        username: str = payload.get("username")
        role: str = payload.get("role")

        if id is None or username is None or role is None:
            raise credentials_exception

        token_data = schema.TokenData(id = id, username=username, role=role)

    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oath2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= "Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token=token, credentials_exception=credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user
