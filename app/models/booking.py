"""
Booking model - for service bookings.
"""
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum


class BookingStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TimelineEnum(str, enum.Enum):
    IMMEDIATE = "IMMEDIATE"
    IN_2_DAYS = "IN_2_DAYS"
    TWO_TO_FIVE_DAYS = "TWO_TO_FIVE_DAYS"


class Booking(Base):
    __tablename__ = "Booking"
    
    id = Column(String, primary_key=True)
    
    userId = Column(String, ForeignKey("User.id"))
    serviceId = Column(String, ForeignKey("Service.id"))
    addressId = Column(String, ForeignKey("Address.id"))
    
    timeline = Column(Enum(TimelineEnum), default=TimelineEnum.IMMEDIATE)
    specialInstructions = Column(String, nullable=True)
    status = Column(Enum(BookingStatusEnum), default=BookingStatusEnum.PENDING)
    
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
    address = relationship("Address", back_populates="bookings")
