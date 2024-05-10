from sqlalchemy import create_engine
from .models import SQLModel
from sqlmodel import Session


def create_tables(database_url: str):
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        print(f"Error creating tables: {e}")


password = "Hemanth888"
username = "postgres"
database = "quiz_stats"
port = 5432
host = "localhost"

database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(database_url)
create_tables(database_url)

session = Session(engine)
