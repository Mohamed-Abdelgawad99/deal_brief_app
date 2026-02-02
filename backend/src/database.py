import os 
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
from src.utils.logger import logger

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/dealbriefs")
logger.info(f"🚀 CONNECTING TO: {DATABASE_URL}")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)