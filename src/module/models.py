from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, BigInteger, ARRAY, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

Base = declarative_base()
metadata = Base.metadata


class Status(PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)
    total_message = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Settings(id={self.id}, total_message={self.total_message})>"


class Verify(Base):
    __tablename__ = 'verify'

    id = Column(BigInteger, primary_key=True)
    guild = Column(BigInteger, unique=True, nullable=False)
    channel_mention = Column(BigInteger, unique=True, nullable=True)
    staff_roles = Column(ARRAY(BigInteger), nullable=True)
    verify_users = relationship('VerifyUsers', back_populates='verify', cascade='all, delete-orphan')

    def __repr__(self):
        return (f"<Verify(id={self.id}, guild={self.guild}, channel_mention={self.channel_mention}, "
                f"staff_roles={self.staff_roles})>")


class VerifyUsers(Base):
    __tablename__ = 'verify_users'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    moder_id = Column(BigInteger, nullable=True)
    guild_id = Column(BigInteger, ForeignKey('verify.guild'), nullable=False)
    status = Column(Enum(Status), nullable=False, default=Status.PENDING)
    rejection = Column(Integer, default=0)
    verification_date = Column(DateTime, nullable=True)
    verify = relationship('Verify', back_populates='verify_users')

    def __repr__(self):
        return (f"<VerifyUsers(id={self.id}, user_id={self.user_id}, moder_id={self.moder_id}, "
                f"guild_id={self.guild_id}, status={self.status}, rejection={self.rejection}, "
                f"verification_date={self.verification_date})>")


class ReportStatus(PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Report(Base):
    __tablename__ = 'report'

    id = Column(BigInteger, primary_key=True)
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.PENDING)
    victim_id = Column(BigInteger, nullable=False)
    perpetrator_id = Column(BigInteger, nullable=False)
    members_id = Column(ARRAY(BigInteger), nullable=True)
    guild_id = Column(BigInteger, nullable=False)
    voice_id = Column(BigInteger, nullable=True)
    channel_id = Column(BigInteger, nullable=True)
    claimed = Column(Boolean, nullable=False, default=False)
    claimed_by = Column(BigInteger, nullable=True)

    def __repr__(self):
        return (
            f"<Report(id={self.id}, status={self.status}, victim_id={self.victim_id}, "
            f"perpetrator_id={self.perpetrator_id}, members_id={self.members_id}, "
            f"guild_id={self.guild_id}, voice_id={self.voice_id}, channel_id={self.channel_id}, "
            f"claimed={self.claimed}, claimed_by={self.claimed_by})>"
        )