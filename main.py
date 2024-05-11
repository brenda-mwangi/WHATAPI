#docker run -v /home/d43m0n4/Desktop/code/openwa-experiment/sessions:/sessions -e PORT=8085 -p 8085:8085 --init openwa/wa-automate -w http://172.17.0.1:8089/items/ --socket
#curl -X POST http://localhost:8085/sendText --data "{\"args\": {\"to\": \"254740730056@c.us\",\"content\": \"Hello World\"}}"

from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
import json
import requests
app = FastAPI()

# Mount static files
@app.post("/items/")
async def create_item(request: Request):
    # Reading and printing request body
    body = await request.body()
    body_json = json.loads(body.decode('utf-8'))
    message_component = {

    }

    if "data" in body_json:
        if "from" in body_json["data"] and "to" in body_json["data"] and "body" in body_json["data"] and "t" in body_json["data"] and "mId" in body_json["data"] and "chat" in body_json["data"]:
            message_component = {
                "from" : body_json["data"]["from"],
                "to" : body_json["data"]["to"],
                "body" : body_json["data"]["body"],
                "messageTime" : body_json["data"]["t"],
                "currentKeyId":body_json["data"]["mId"],
                "lastKeyId":body_json["data"]["chat"]["lastReceivedKey"]["id"]
            }

            payload = {
                "args": {
                    "to": "254776170839@c.us",
                    "content": "Hello World!"
                }
            }
            response = requests.post("http://localhost:8085/sendText", json=payload)
            print(response.text)
    return True

if __name__=="__main__":
    uvicorn.run(host="0.0.0.0", port=8089, app="main:app", reload=True)
