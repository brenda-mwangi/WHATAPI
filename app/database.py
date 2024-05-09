from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "postgresql://<username>:<password>@<ip-address/hostname>/<database-name>"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:ahH38*$n@changalink.c372mljr1knp.eu-west-2.rds.amazonaws.com/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)  #resposible for connecting sqlalchemy to the database

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        print("[*] Connection success")
        yield db
    finally:
        print("[*] Connection closed")
        db.close()
