from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger
from app.database import Base
from datetime import datetime, timedelta


# each model(class) refers to a table in our database
def default_date():
    return int((datetime.now()).timestamp())

def default_end_date():
    return int((datetime.now() + timedelta(days=7)).timestamp())

class User(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    __tablename__ = "changalink_users"
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
