from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, BigInteger, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True) # Telegram User ID
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    is_premium = Column(Boolean, default=False)
    premium_expiry = Column(DateTime, nullable=True)
    is_suspended = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    clones = relationship("Clone", back_populates="owner")

class Clone(Base):
    __tablename__ = "clones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(BigInteger, ForeignKey("users.id"))
    bot_token = Column(String(255), unique=True, nullable=False) # Should be encrypted in production
    bot_username = Column(String(255), nullable=True)
    bot_name = Column(String(255), nullable=True)
    status = Column(String(50), default="active") # active, suspended, stopped
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_active = Column(DateTime, nullable=True)

    settings = relationship("CloneSettings", back_populates="clone", uselist=False)
    owner = relationship("User", back_populates="clones")

class CloneSettings(Base):
    __tablename__ = "clone_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clone_id = Column(Integer, ForeignKey("clones.id"))
    welcome_text = Column(Text, nullable=True)
    welcome_media = Column(String(255), nullable=True)
    inline_buttons = Column(JSON, nullable=True)
    assistant_name = Column(String(255), nullable=True)
    assistant_bio = Column(Text, nullable=True)
    start_message = Column(Text, nullable=True)
    fallback_message = Column(Text, nullable=True)
    support_link = Column(String(255), nullable=True)
    custom_footer = Column(String(255), nullable=True)

    clone = relationship("Clone", back_populates="settings")

class Broadcast(Base):
    __tablename__ = "broadcasts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(BigInteger) # User ID who initiated
    clone_id = Column(Integer, ForeignKey("clones.id"), nullable=True) # Null for Supreme Panel global broadcast
    message_data = Column(JSON) # The content to broadcast
    status = Column(String(50), default="pending") # pending, processing, completed, failed
    total_users = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    blocked_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AdminAction(Base):
    __tablename__ = "admin_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger)
    action = Column(String(255))
    target_id = Column(BigInteger, nullable=True)
    reason = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True)
    is_enabled = Column(Boolean, default=True)
    tenant_id = Column(Integer, nullable=True) # If null, global
