from sqlalchemy import create_engine
from sqlmodel import Session
from .models import SQLModel

def create_tables(database_url: str):
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        print(f"Error creating tables: {e}")

database_url = "sqlite:///quiz_stats.db"
engine = create_engine(database_url)
create_tables(database_url)
session = Session(engine)