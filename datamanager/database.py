import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DB_PASSWORD = os.environ.get('DB_PASSWORD')
SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://postgres:{DB_PASSWORD}@127.0.0.1:5432/HarmonApp-v1.1'

engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# # Inspect the database and list tables
# inspector = inspect(engine)
# tables = inspector.get_table_names()
# print("Tables in the database:", tables)
