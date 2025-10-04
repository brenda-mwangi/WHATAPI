from app import models, schema, oath2
from app.database import get_db
from app.utils import templates
from fastapi.responses import HTMLResponse

from fastapi import APIRouter, status, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

router = APIRouter(
        prefix="/bot",
        tags=['Bot Operations']
)

@router.get("/")
def bot_home():
    return {"Hello": "world"}

@router.get("/create-bot", response_class=HTMLResponse, summary="Create Bot page")
def create_bot_page(request: Request, db: Session = Depends(get_db), logged_in_user: models.User = Depends(oath2.get_current_user)):#,logged_in_user: int = Depends(oath2.get_current_user)):
    """
    Endpoint to serve create a new bot account.
    """
    return templates.TemplateResponse("working.html", {"request": request})

# @router.get("/create-bot/{user_id}")
# def create_bot(user_id: int):
#     # Process with the user_id
#     return {"message": f"Bot creation page for user {user_id}"}

# @router.get("/create-bot/{user_id}", status_code=status.HTTP_201_CREATED, response_model=schema.UpdateUser, summary="User's Home")
# def create_bot(user_id: int, db: Session = Depends(get_db), logged_in_user: int = Depends(oath2.get_current_user)):
#     """ Endpoint to fetch user's home data. """

#     user_query = db.query(models.User).filter(models.User.id == user_id)
#     user = user_query.first()

#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     elif user.id != logged_in_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="You are not authorized to perform that action",
#         )
#     else:
#         user_data = user.dict()

#     return FileResponse('../index.html')


# @router.post("/create_link", status_code=status.HTTP_201_CREATED, response_model=schema.LinkResponse)
# async def create_link(changalink: schema.LinkBase, db: Session = Depends(get_db)):  #, logged_in_user: int = Depends(oath2.get_current_user)):
#     try:
#         new_link = models.ChangaLink(**changalink.dict())

#         db.add(new_link)
#         db.commit()
#         db.refresh(new_link)
#         return new_link

#     except IntegrityError as e:
#         db.rollback()
#         raise HTTPException(detail = "Please try again", status_code = status.HTTP_400_BAD_REQUEST)

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(detail="Invalid link data", status_code=status.HTTP_400_BAD_REQUEST)

# @router.delete("/delete_link/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_link(link_id: str, db: Session = Depends(get_db), logged_in_user: int = Depends(oath2.get_current_user)):
#     link = db.query(models.ChangaLink).filter(models.ChangaLink.id == link_id).first()

#     if link == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
#     else:
#         if link.owner_id != logged_in_user.id:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform that action")
#         else:
#             db.delete(link)
#             db.commit()

# @router.put("/update_link/{link_id}", status_code=status.HTTP_200_OK, response_model=schema.UpdateLink)
# def update_link(link: schema.UpdateLink, link_id: str, db: Session = Depends(get_db), logged_in_user: int = Depends(oath2.get_current_user)):
#     link_query = db.query(models.ChangaLink).filter(models.ChangaLink.id == link_id)

#     link_details = link_query.first()

#     if link_details == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not update ChangaLink since it was not found")
#     else:
#         if link_details.owner_id != logged_in_user.id:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform that action")
#         else:
#             link_data = link.dict()

#             for key in link_data.keys():
#                 if key not in ["title","description","mode_of_beneficiary_payment","beneficiary_phone","target_amount"]:
#                     raise ValueError(f'Invalid entry found: {key}. Only "title","description","mode_of_beneficiary_payment","beneficiary_phone","target_amount" are allowed.')
#                 else:
#                     try:
#                         if link_data[key] is None or link_data[key] == '':
#                             pass
#                         else:
#                             link_query.update({key: link_data[key]})
#                             db.commit()

#                     except Exception as e:
#                         print({key: e})

#         return link_details
