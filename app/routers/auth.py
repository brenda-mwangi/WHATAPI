# file to handle authentications
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, utils, oath2
from app.schema import Token

router = APIRouter(
    prefix= "/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=Token, include_in_schema=False)
async def login(user_creds: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user_query = db.query(models.User).filter(models.User.phone == user_creds.username).first()

    if user_query:
        if not utils.verify_password(user_creds.password, user_query.password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
        else:
        #create access token
            # if user_query.is_logged_in:
            #     return HTTPException(status_code=409, detail="User is already logged in.")
            # else:
                try:
                    access_token = oath2.create_access_token(data = {
                                                                "id": user_query.id,
                                                                "username": user_query.firstname,
                                                                "role": user_query.role
                                                                } )
                    # user_query.is_logged_in = True
                    # db.commit()
                    return {"access_token": access_token, "token_type": "Bearer"}

                except Exception as e:
                    db.rollback()
                    raise HTTPException(detail=e)

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")


