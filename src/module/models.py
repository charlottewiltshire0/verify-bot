from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum


Base = declarative_base()


class Status(PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)
    total_message = Column(Integer, nullable=False, default=0)


class Verify(Base):
    __tablename__ = 'verify'

    id = Column(Integer, primary_key=True)
    guild = Column(Integer, unique=True, nullable=False)
    channel_mention = Column(String, unique=True, nullable=True)
    verify_users = relationship('VerifyUsers', back_populates='verify', cascade='all, delete-orphan')


class VerifyUsers(Base):
    __tablename__ = 'verify_users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    moder_id = Column(Integer, nullable=True)
    verify_id = Column(Integer, ForeignKey('verify.id'), nullable=False)
    status = Column(Enum(Status), nullable=False, default=Status.PENDING)
    rejection = Column(Integer, default=0)
    verification_date = Column(DateTime, nullable=True)
    verify = relationship('Verify', back_populates='verify_users')