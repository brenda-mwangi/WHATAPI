# changabox,changalink
#docker run -v /home/d43m0n4/Desktop/code/openwa-experiment/sessions:/sessions -e PORT=8085 -p 8085:8085 --init openwa/wa-automate -w http://172.17.0.1:8089/items/ --socket

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from models import Base
from database import engine

from sys import path
# path.append("/home/d43m0n4/Desktop/code/WhatAPI")
# path.append("/opt/render/project/src/")
path.append("/Users/charles/Desktop/code/WhatAPI") #macos
from routers import users, links, auth, WA_bridge

Base.metadata.create_all(bind=engine)
tags_metadata = [
    {
        "name": "User",
        "description": "Operations for **users only**",
    },
    {
        "name": "Link",
        "description": "Manage Links only.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
    {
        "name": "Authentication",
        "description": "Manage authentication",
    }
]
description = "The FundraiserBot is an innovative automated system meticulously crafted to revolutionize fundraising endeavors through the ubiquitous WhatsApp platform. It streamlines and simplifies the fundraising process by seamlessly integrating with WhatsApp, enabling effortless donation collection, transparent tracking of funds, and efficient communication with donors and beneficiaries. Its robust functionalities encompass personalized donation campaigns, real-time progress updates, and secure handling of contributions, empowering organizations and individuals to initiate and manage successful fundraising initiatives effortlessly."
app = FastAPI(
    title="Changalink API Documentation",
    description=description,
    summary='"Empowering Causes, One Message at a Time."',
    version="1.0.",
    terms_of_service="http://changalink.bdigismat.com/terms/",
    contact={
        "name": "Brenda Mwangi",
        "url": "http://changalink.bdigismat.com/contact/",
        "email": "brenda@changalink.bdigismat.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    docs_url=None,
    redoc_url="/v2/popnplay",
    openapi_tags=tags_metadata,
              )

# static_path = os.path.join(os.path.dirname(__file__), "static")
# app.mount("/static", StaticFiles(directory=static_path), name="static")

app.include_router(links.router)
app.include_router(users.router)
app.include_router(WA_bridge.router)
app.include_router(auth.router)

if __name__ == "__main__":
    uvicorn.run(host="localhost", reload=True, app="main:app")
