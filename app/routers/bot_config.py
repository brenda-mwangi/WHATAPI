import json
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
def create_bot_page(request: Request, db: Session = Depends(get_db)):#, logged_in_user: models.User = Depends(oath2.get_current_user), token: str = Depends(oath2.oath2_scheme)):
    """
    Endpoint to serve create a new bot account.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/save-configuration")
async def save_bot_configuration(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oath2.get_current_user),
    token: str = Depends(oath2.oath2_scheme)  # Add this line to get the access token
):
    """Save bot configuration from the builder"""
    data = await request.json()
    print("Logged in user:", current_user)
    print("Access token:", token)
    
    bot = models.Bot(
        owner_id=current_user.id,  # Change this from ['id'] to .id
        name=data.get('bot_name', 'My Bot'),
        phone_number=data.get('phone_number'),
        configuration=json.dumps(data.get('menu_structure', []))
    )
    
    # db.add(bot)
    # db.commit()
    # db.refresh(bot)
    
    return {
        "bot_id": bot.id,
        "webhook_url": f"/bot-runtime/webhook/{bot.id}"
    }

# @router.get("/create-bot/{user_id}")
# def create_bot(user_id: int):
#     # Process with the user_id
#     print(f"Creating bot for user ID: {user_id}")
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

# @router.post("/create-bot", status_code=status.HTTP_201_CREATED, response_model=schema.ShowBot, summary="Create a new bot")
# def create_bot(bot: schema.Bot, db: Session = Depends(get_db), logged_in_user: models.User = Depends(oath2.get_current_user)):
#     """ Endpoint to create a new bot account. """

#     try:
#         new_bot = models.Bot(owner_id=logged_in_user.id, **bot.dict())
#         db.add(new_bot)
#         db.commit()
#         db.refresh(new_bot)
#     except IntegrityError as e:
#         db.rollback()
#         if 'unique constraint' in str(e.orig):
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bot with this name already exists.")
#         else:
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the bot.")

#     return new_bot