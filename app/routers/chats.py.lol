from fastapi import APIRouter, Response, Request
from twilio.twiml.messaging_response import MessagingResponse
import json
import hashlib
import os

router = APIRouter(prefix="/chat", tags=['Chat'])

# Load chat configuration from JSON file
with open(os.getenv('CHAT_CONFIG_PATH', 'app/chat.json'), 'r') as file:
    chat_config = json.load(file)

# In-memory store for user states
user_states = {}

@router.post('/receive')
async def bot(request: Request):
    form_data = await request.form()
    incoming_msg = form_data.get('Body', '').lower()
    from_number = form_data.get('From')
    resp = MessagingResponse()
    msg = resp.message()

    session_id = hashlib.md5(from_number.encode()).hexdigest()
    user_input = user_states.get(session_id, [])
    print(user_input)
    # Process input
    user_input.append(incoming_msg)
    user_states[session_id] = user_input
    print(user_input)

    if not user_input or any(incoming_msg in trigger for trigger in chat_config['trigger']):
        msg.body(chat_config["greeting"] + chat_config["main"])
        user_states[session_id] = []  # Reset session
    else:
        # Determine the chat option based on the first input
        chat_option = user_input[0]
        if chat_option in chat_config:
            response = chat_config[chat_option][min(len(user_input), len(chat_config[chat_option])) - 1]
            msg.body(response)
            if response == chat_config[chat_option][-1]:  # Last step in the option
                user_states[session_id] = []  # Reset session
        else:
            msg.body("Invalid option. Please choose a valid option from the menu.")

    return Response(content=str(resp), media_type="application/xml")

# ... Rest of your code ...
# from fastapi import APIRouter, status, Depends, HTTPException, Request, Response
# from app import models, schema, oath2
# from app.database import get_db
# from twilio.rest import Client
# from twilio.twiml.messaging_response import MessagingResponse
# import json, os
# import hashlib
# from app.utils import clear_chat
# # , chat_create_link

# router = APIRouter(
#         prefix="/chat",
#         tags=['Chat']
# )

# # Load chat configuration from JSON file
# with open('app/chat.json', 'r') as file:
#     chat_config = json.load(file)

# # In-memory store for user states
# user_states = {}

# @router.post('/receive')
# async def bot(request: Request):
#     form_data = await request.form()
#     incoming_msg = form_data.get('Body', '').lower()
#     from_number = form_data.get('From')
#     resp = MessagingResponse()
#     msg = resp.message()
#     text = ""

#     session_id = hashlib.md5(from_number.encode()).hexdigest()
    
#     ## remember to add logic for back navigation
#     with open(session_id, 'r+') as file:
#         text = file.read()
#         if text == "":

#             text = incoming_msg
#         else:
#             text = text+"*"+incoming_msg
    
#         file.seek(0)
#         file.write(text)
#         file.truncate()

#         if text is not None:  # Check if text is not None
#             if '*' in text:
#                 text = text.split("*")
#             else:
#                 text = text.split()

#             if text == "" or not text or any(trigger in incoming_msg for trigger in chat_config['trigger']):
#                 msg.body(chat_config["greeting"]+chat_config["main"])
#                 #clear session data
#                 clear_chat(file)
#             elif text[0] == "1":
#                 if len(text) == 1:
#                     msg.body(chat_config["start_fundraiser"][0])
#                 elif len(text) == 2:
#                     msg.body(chat_config["start_fundraiser"][1])
#                 elif len(text) == 3:
#                     msg.body(chat_config["start_fundraiser"][2])
#                 elif len(text) == 4:
#                     msg.body(chat_config["start_fundraiser"][3])
#                 elif len(text) == 5:
#                     msg.body(chat_config["start_fundraiser"][4])
#                 elif len(text) == 6:
#                     msg.body(chat_config["start_fundraiser"][5])
#                     # chat_create_link(text[1], text[2], text[3], text[4], text[5])
#                     clear_chat(file)
#                     msg.body(chat_config["greeting"]+chat_config["main"])
                    
#             elif text[0] == "2":
#                 if len(text) == 1:
#                     msg.body(chat_config["donate_to_fundraiser"][0])
#                 elif len(text) == 2:
#                     msg.body(chat_config["donate_to_fundraiser"][1])
#                 elif len(text) == 3:
#                     msg.body(chat_config["donate_to_fundraiser"][2])
#                     clear_chat(file)
#             elif text[0] == "3":
#                 if len(text) == 1:
#                     msg.body(chat_config["check_fundraiser_status"][0])
#                 elif len(text) == 2:
#                     msg.body(chat_config["check_fundraiser_status"][1])
#                 elif len(text) == 3:
#                     msg.body(chat_config["check_fundraiser_status"][2])
#                     clear_chat(file)
#             elif text[0] == "4":
#                 if len(text) == 1:
#                     msg.body(chat_config["update_fundraiser"][0])
#                 elif len(text) == 2:
#                     msg.body(chat_config["update_fundraiser"][1])
#                 elif len(text) == 3:
#                     msg.body(chat_config["update_fundraiser"][2])
#                     clear_chat(file)
#             elif text[0] == "5":
#                 if len(text) == 1:
#                     msg.body(chat_config["delete_fundraiser"][0])
#                 elif len(text) == 2:
#                     msg.body(chat_config["delete_fundraiser"][1])
#                 elif len(text) == 3:
#                     msg.body(chat_config["delete_fundraiser"][2])
#                     clear_chat(file)
#             elif text[0] == "6":
#                 if len(text) == 1:
#                     msg.body(chat_config["help_support"][0])
#                 elif len(text) == 2:
#                     msg.body(chat_config["help_support"][1])
#                 elif len(text) == 3:
#                     msg.body(chat_config["help_support"][2])
#                     clear_chat(file)

#     return Response(content=str(resp), media_type="application/xml")























































































# @router.get("/")
# def link_home():
#     return {"Hello": "world"}

# @router.post("/receive", status_code=status.HTTP_200_OK)
# # def delete_link(link_id: str, db: Session = Depends(get_db), logged_in_user: int = Depends(oath2.get_current_user)):
# async def receive_chat(request: Request):
#     form_data = await request.form()
#     sender = form_data.get("From")
#     reciepient = form_data.get("To")
#     message = form_data.get("Body")

#     session_txt = session_txt +"*"+message 

#     account_sid = ''
#     auth_token = ''
#     client = Client(account_sid, auth_token)

#     resp = f'''<?xml version="1.0" encoding="UTF-8"?>
# <Response>
#     <Message>Your appointment is coming up on July 21 at 3PM. Mark this tweet for future.</Message>
# </Response>'''

#     return Response(content=resp, media_type="application/xml")

