from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger
from database import Base
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
    username = Column(String(length=50), nullable=False)
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
    
# class ChangaLink(Base):
#     __tablename__ = 'changalinks'
#     __table_args__ = {'extend_existing': True}

#     id = Column(String, unique=True, primary_key=True, nullable= False, default=None)
#     owner_id = Column(Integer, ForeignKey("changalink_users.id", ondelete="CASCADE"),nullable= False)
#     title = Column(String(length=70), nullable= False)
#     description = Column(String,nullable= False)
#     mode_of_beneficiary_payment = Column(String(length=6), nullable=False)
#     beneficiary_phone = Column(String(length=13), nullable=False)
#     target_amount = Column(Integer, nullable=True)
#     total_amount_collected = Column(Integer, default=0)
#     is_active = Column(Boolean, nullable= False, default=True)
#     date_started = Column(BigInteger, nullable=False, default=default_date)
#     date_ended = Column(BigInteger, nullable=False, default=default_end_date)

#     # our_percentage = Column(Float)
#     # date_started = Column(TIMESTAMP(timezone =True), nullable= False, default = datetime.utcnow())
#     # date_end = Column(TIMESTAMP, default=datetime.now() + timedelta(days=7), nullable=False)
#     # date_end = Column(DateTime, default=datetime.now(timezone(timedelta(hours=3))) + timedelta(days=7), nullable=False)
