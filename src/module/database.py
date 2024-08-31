from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from .yml import Yml
from loguru import logger

config = Yml('./config/config.yml')
data = config.read()
DATABASE_TYPE = data.get('Storage', {}).get("Type", "").lower()
DATABASE_URL = data.get('Storage', {}).get("URL", "")

if DATABASE_TYPE == "postgres":
    engine = create_engine(url=DATABASE_URL, connect_args={"connect_timeout": 10})
elif DATABASE_TYPE == "sqlite":
    engine = create_engine(url=DATABASE_URL, connect_args={"check_same_thread": False})
else:
    raise ValueError("Unsupported database type specified in the configuration.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    from .models import Base
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
    except SQLAlchemyError as e:
        logger.info(f"An error occurred during table initialization: {e}")