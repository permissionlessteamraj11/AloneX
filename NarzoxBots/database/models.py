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
    is_sudo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    clones = relationship("Clone", back_populates="owner")

class Chat(Base):
    __tablename__ = "chats"

    id = Column(BigInteger, primary_key=True)
    title = Column(String(255), nullable=True)
    lang = Column(String(10), default="en")
    admin_only = Column(Boolean, default=False)
    cmd_delete = Column(Boolean, default=False)
    is_blacklisted = Column(Boolean, default=False)

class Clone(Base):
    __tablename__ = "clones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(BigInteger, ForeignKey("users.id"))
    bot_token = Column(String(255), unique=True, nullable=False)
    bot_username = Column(String(255), nullable=True)
    bot_name = Column(String(255), nullable=True)
    status = Column(String(50), default="active")
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
    assistant_session = Column(Text, nullable=True)
    start_message = Column(Text, nullable=True)
    fallback_message = Column(Text, nullable=True)
    support_link = Column(String(255), nullable=True)
    updates_link = Column(String(255), nullable=True)
    owner_link = Column(String(255), nullable=True)
    group_link = Column(String(255), nullable=True)
    clone_link = Column(String(255), nullable=True)
    source_link = Column(String(255), nullable=True)
    theme = Column(String(100), nullable=True)
    thumbnail = Column(String(255), nullable=True)
    custom_footer = Column(String(255), nullable=True)

    clone = relationship("Clone", back_populates="settings")

class GlobalSettings(Base):
    __tablename__ = "global_settings"

    id = Column(Integer, primary_key=True, default=1)
    welcome_banner = Column(String(255), nullable=True)
    help_banner = Column(String(255), nullable=True)
    support_link = Column(String(255), default="https://t.me/zolvid")
    updates_link = Column(String(255), default="https://t.me/zolvid")
    owner_link = Column(String(255), default="https://t.me/zolvid")

class Broadcast(Base):
    __tablename__ = "broadcasts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(BigInteger)
    clone_id = Column(Integer, ForeignKey("clones.id"), nullable=True)
    message_data = Column(JSON)
    status = Column(String(50), default="pending")
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
