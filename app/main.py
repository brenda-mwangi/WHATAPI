import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from app.models import Base
from app.database import engine
from app.oath2 import SECRET_KEY
from app.routers import services, users, auth, bot_config

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

Base.metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "Authentication",
        "description": "User login, signup, and account management",
    },
    {
        "name": "Bots",
        "description": "Create, update, and manage WhatsApp bots for your business",
    },
    {
        "name": "WhatsApp Integration",
        "description": "Connect and verify WhatsApp numbers, link bots to phone numbers",
    },
    {
        "name": "AI Integration",
        "description": "Integrate AI capabilities into your WhatsApp bots for enhanced interactions",
    },
#     {
#         "name": "Chat Simulation",
#         "description": "Test and debug your bot conversations before going live",
#     },
#     {
#         "name": "Billing",
#         "description": "Manage subscriptions, plans, and quotas",
#     },
]
description = """
**WhatsApp Bot SaaS Platform** 🚀

This API powers a multi-tenant SaaS platform for businesses to build, test, and deploy WhatsApp bots.  
Features include:
- Secure user accounts and multi-tenant support  
- Easy bot creation and stateful chatbot flows  
- Sandbox for testing messages  
- Direct integration with WhatsApp numbers  
- Subscription & billing management  
"""
app = FastAPI(
    title="WhatsApp Bot SaaS API",
    description=description,
    summary="All-in-one WhatsApp chatbot SaaS backend",
    version="1.0.0",
    terms_of_service="https://whatsapp.kriftx.app/terms/",
    contact={
        "name": "Your Company",
        "url": "https://whatsapp.kriftx.app",
        "email": "support@whatsapp.kriftx.app",
    },
    license_info={
        "name": "Commercial License",
        "url": "https://whatsapp.kriftx.app/license",
    },
    docs_url=None,
    redoc_url="/v1/docs",
    openapi_tags=tags_metadata,
)

# Serve static files
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.include_router(services.router)
app.include_router(users.router)
app.include_router(bot_config.router)
app.include_router(auth.router)

# # 🔥 Add a route lister
# @app.get("/routes", tags=["Debug"])
# async def list_routes():
#     return [
#         {
#             "path": route.path,
#             "name": route.name,
#         }
#         for route in app.router.routes
#     ]
