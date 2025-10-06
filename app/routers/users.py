from fastapi import status, Depends, HTTPException, APIRouter, Request, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from datetime import datetime
from jose import jwt
from app import models, oath2, schema, utils
from app.database import get_db
from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
import os

router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={404: {"description": "Not Found"}},
)


@router.get("/", summary="User's Home")
@router.get("/home", summary="User's Home")
def user_home():
    """
    Endpoint to fetch user's home data.
    """
    return {"Hello": "user"}

@router.get("/signup", response_class=HTMLResponse, summary="Signup page")
def create_user_account_page(request: Request):
    """
    Endpoint to serve create a new user account page.
    """
    return utils.templates.TemplateResponse("signup.html", {"request": request})

@router.post( "/create-account", status_code=status.HTTP_201_CREATED, response_model=schema.UserResponse, summary="Create User Account")
async def create_user_account(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """
    Endpoint to create a new user account.
    """
    hashed_password = utils.hash(password)  # Ensure you have a function to hash passwords properly

    try:
        # Create a new user instance using the models.User model
        new_user = models.User(username=username, email=email, password=hashed_password)

        # Add the new user to the database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Return the new user
        return new_user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username is already in use",
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user data"
        )


@router.delete(
    "/delete_account/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete User Account",
)
def delete_user_account(
    user_id: int,
    db: Session = Depends(get_db),
    logged_in_user: int = Depends(oath2.get_current_user),
):
    """
    Endpoint to delete a user account.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    elif user.id != logged_in_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform that action",
        )
    else:
        db.delete(user)
        db.commit()


@router.put(
    "/update_account/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=schema.UpdateUser,
    summary="Update User Account",
)
def update_user_account(user_update: schema.UpdateUser,
    user_id: int,
    db: Session = Depends(get_db),
    logged_in_user: int = Depends(oath2.get_current_user),
):
    """
    Endpoint to update a user account.
    """
    user_update.password = utils.hash(user_update.password)

    user_query = db.query(models.User).filter(models.User.id == user_id)
    user = user_query.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    elif user.id != logged_in_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform that action",
        )
    else:
        user_data = user_update.dict()

        for key in user_data.keys():
            if key not in ["firstname", "lastname", "password"]:
                raise ValueError(
                    f"Invalid entry found: {key}. Only 'firstname', 'lastname' and 'password' are allowed."
                )
            else:
                try:
                    if user_data[key] is not None and user_data[key] != "":
                        user_query.update({key: user_data[key]})
                        db.commit()

                except Exception as e:
                    return {key: e}

    return user


@router.get("/logout", summary="User Logout")
# def logout(request: Request, token: str = Depends(oath2.oath2_scheme), db: Session = Depends(get_db)):
def logout(request: Request):
    """
    Endpoint to logout a user by blacklisting their authentication token.
    """
    try:
        # request.session['user'] = False
        # request.session['access_token'] = False
        request.cookies.clear("access_token")

        # payload = oath2.jwt.decode(token, oath2.SECRET_KEY, algorithms=[oath2.ALGORITHM])
        # expiration_date = payload.get('exp')
        # db.add(models.TokenBlacklist(token=token, expires_at=datetime.fromtimestamp(expiration_date)))
        # db.commit()
        return {"message": "Logged out successfully"}
    except oath2.jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except oath2.jwt.JWTError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))