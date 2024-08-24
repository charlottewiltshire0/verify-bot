from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, BigInteger, ARRAY, Boolean, func
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
    role_id = Column(BigInteger, nullable=True)
    status = Column(Enum(Status), nullable=False, default=Status.PENDING)
    rejection = Column(Integer, default=0)
    verification_date = Column(DateTime, nullable=True)
    verify = relationship('Verify', back_populates='verify_users')
    last_moder_id = Column(BigInteger, nullable=True)
    last_verification_date = Column(DateTime, nullable=True)

    def __repr__(self):
        return (f"<VerifyUsers(id={self.id}, user_id={self.user_id}, moder_id={self.moder_id}, "
                f"guild_id={self.guild_id}, status={self.status}, rejection={self.rejection}, "
                f"verification_date={self.verification_date}), last_moder_id={self.last_moder_id}, "
                f"last_verification_date={self.last_verification_date})>, role_id={self.role_id}")


class ReportStatus(PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Report(Base):
    __tablename__ = 'reports'

    id = Column(BigInteger, primary_key=True)
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.PENDING)
    victim_id = Column(BigInteger, nullable=False)
    perpetrator_id = Column(BigInteger, nullable=False)
    member_ids = Column(ARRAY(BigInteger), nullable=True)
    message_id = Column(BigInteger, nullable=True)
    guild_id = Column(BigInteger, nullable=False)
    reason = Column(String, nullable=True)
    voice_channel_id = Column(BigInteger, nullable=True)
    text_channel_id = Column(BigInteger, nullable=True)
    is_claimed = Column(Boolean, nullable=False, default=False)
    claimed_by_user_id = Column(BigInteger, nullable=True)
    closed_by_user_id = Column(BigInteger, nullable=True)
    closed_at = Column(DateTime, nullable=True, default=func.now())

    def __repr__(self):
        return (
            f"<Report(id={self.id}, status={self.status}, victim_id={self.victim_id}, "
            f"perpetrator_id={self.perpetrator_id}, member_ids={self.member_ids}, "
            f"guild_id={self.guild_id}, voice_channel_id={self.voice_channel_id}, text_channel_id={self.text_channel_id}, "
            f"is_claimed={self.is_claimed}, claimed_by_user_id={self.claimed_by_user_id}, "
            f"closed_by_user_id={self.closed_by_user_id}, closed_at={self.closed_at})>, reason={self.reason}"
        )


class BanStatus(PyEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class Ban(Base):
    __tablename__ = 'ban'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    ban_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    reason = Column(String, nullable=True)
    proof = Column(String, nullable=True)
    moderator_id = Column(BigInteger, nullable=False)
    status = Column(Enum(BanStatus), nullable=False, default=BanStatus.ACTIVE)
    revoked_by = Column(BigInteger, nullable=True)
    revoked_date = Column(DateTime, nullable=True)

    def __repr__(self):
        return (
            f"<Ban(id={self.id}, user_id={self.user_id}, guild_id={self.guild_id}, "
            f"ban_date={self.ban_date}, expiration_date={self.expiration_date}, "
            f"reason={self.reason}, proof={self.proof}, moderator_id={self.moderator_id}, "
            f"status={self.status}, revoked_by={self.revoked_by}, revoked_date={self.revoked_date})>"
        )
