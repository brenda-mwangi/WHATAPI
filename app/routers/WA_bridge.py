from fastapi import APIRouter, Request
router = APIRouter()


@router.post("/bridge")
async def middleware(request: Request):
    payload = await request.json()
    print(payload)
    if payload["messageBody"]:
        pass
    return {"message": "Hello, world!"}

# @router.post("/create_link", status_code=status.HTTP_201_CREATED, response_model=schema.LinkResponse)
# async def create_link(changalink: schema.LinkBase, db: Session = Depends(get_db), logged_in_user: int = Depends(oath2.get_current_user)):
#     try:
#         new_link = models.ChangaLink(
#             owner_id=logged_in_user.id, **changalink.dict())

#         db.add(new_link)
#         db.commit()
#         db.refresh(new_link)
#         return new_link

#     except IntegrityError as e:
#         db.rollback()
#         raise HTTPException(detail="Please try again",
#                             status_code=status.HTTP_400_BAD_REQUEST)

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(detail="Invalid link data",
#                             status_code=status.HTTP_400_BAD_REQUEST)
