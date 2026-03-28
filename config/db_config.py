import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv 
from os.path import join, dirname

dotenv_path = join(dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)
# Provide defaults to prevent "None" string errors
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = int(os.getenv("DATABASE_PORT"))
DATABASE_NAME = os.getenv("DATABASE_NAME")



DATABASE_URL = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]