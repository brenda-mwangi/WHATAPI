from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger, Text, ForeignKey
from app.database import Base
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship


# each model(class) refers to a table in our database
def default_date():
    return int((datetime.now()).timestamp())

def default_end_date():
    return int((datetime.now() + timedelta(days=7)).timestamp())

class User(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, primary_key=True, nullable= False, default=None)
    username = Column(String(length=50), unique=True, nullable=False)
    email = Column(String(length=320), nullable=False, unique=True)
    password = Column(String(length=255), nullable=False)
    role = Column(String(length=50), nullable=False, default="User")
    is_logged_in = Column(Boolean, nullable= False, default=False)
    time_registered = Column(BigInteger, nullable=False, default=default_date)

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, primary_key=True, nullable= False, default=None)
    token = Column(String, unique=True)
    expires_at = Column(DateTime, default=default_date)

class Bot(Base):
    __tablename__ = "bots"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(20), unique=True)  # WhatsApp number linked to bot
    configuration = Column(Text, nullable=False)  # JSON menu structure
    is_active = Column(Boolean, default=True)
    created_at = Column(BigInteger, default=default_date)
    
    # Store conversation states
    owner = relationship("User", backref="bots")

class BotSession(Base):
    __tablename__ = "bot_sessions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey('bots.id'))
    user_phone = Column(String(20), nullable=False)  # WhatsApp user
    current_menu_code = Column(String(50))  # Current position in menu tree
    collected_data = Column(Text)  # JSON of collected inputs
    last_interaction = Column(BigInteger, default=default_date)
    
    bot = relationship("Bot", backref="sessions")