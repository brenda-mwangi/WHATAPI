from fastapi import status, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app import models, oath2, schema, utils
from app.database import get_db

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


@router.post( "/create-account", status_code=status.HTTP_201_CREATED, response_model=schema.UserResponse, summary="Create User Account")
def create_user_account(user: schema.UserBase, db: Session = Depends(get_db)):
    """
    Endpoint to create a new user account.
    """
    user.password = utils.hash(user.password)

    try:
        new_user = models.User(**user.dict())

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already in use",
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
def update_user_account(
    user_update: schema.UpdateUser,
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
