from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
import uuid


class User(Base):
    __tablename__= "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    predictions = relationship("PredictionHistory", back_populates="user")
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    health_profile = relationship("UserHealthProfile", back_populates="user", uselist=False)
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    
    
    
class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    input_data = Column(String)       # JSON stored as string
    prediction = Column(String)       # predicted obesity level
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationship back to user
    user = relationship("User", back_populates="predictions")

class passwordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User")


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    gender = Column(String, nullable=True)
    height_m = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class UserHealthProfile(Base):
    __tablename__ = "user_health_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    # Core Info
    gender = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    height_m = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)

    # Lifestyle & Habits
    family_overweight_history = Column(String, nullable=True)
    high_calorie_food = Column(String, nullable=True)
    vegetable_intake_freq = Column(Integer, nullable=True)
    main_meals_per_day = Column(Integer, nullable=True)
    snack_frequency = Column(String, nullable=True)
    smokes = Column(String, nullable=True)
    water_intake_liters = Column(Float, nullable=True)
    calorie_tracking = Column(String, nullable=True)
    physical_activity_hours = Column(Float, nullable=True)
    screentime_hours = Column(Float, nullable=True)
    alcohol_consumption = Column(String, nullable=True)
    travel_mode = Column(String, nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="health_profile")



class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String, nullable=False)  # ← ADD THIS
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")



class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    
    role = Column(String, nullable=False)  
    content = Column(String, nullable=False)
    sources = Column(String, nullable=True) 
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    session = relationship("ChatSession", back_populates="messages")