from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base
from .yml import Yml

config = Yml('./config/config.yml')
data = config.read()
DATABASE_URL = data.get('Storage', {}).get("URL", {})

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
