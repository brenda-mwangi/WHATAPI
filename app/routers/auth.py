# file to handle authentications
from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, utils, oath2
from app.schema import Token

router = APIRouter(
    prefix= "/auth",
    tags=["Authentication"]
)

# @router.get("/auth/verify")
# def verify_token(token: str = Depends(oath2.oath2_scheme)):
#     try:
#         user = oath2.verify_access_token(token)
#         return {"message": "Token is valid", "user": user}
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=Token, include_in_schema=False)
async def login(request: Request, user_creds: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user_query = db.query(models.User).filter(models.User.username == user_creds.username).first()
    print(user_query.id)
    if user_query:
        if not utils.verify_password(user_creds.password, user_query.password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
        else:
            try:
                access_token = oath2.create_access_token(data = {
                    "id": user_query.id,
                    "username": user_query.username,
                    "role": user_query.role
                    } )

                request.session['user'] = user_creds.username
                request.session['access_token'] = access_token

                return RedirectResponse(url="/bot/create-bot", status_code=303)


            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e)

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

