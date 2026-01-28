"""
Service model - services offered by workers.
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Enum, ForeignKey, ARRAY, Numeric
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum


class PriceTypeEnum(str, enum.Enum):
    HOURLY = "HOURLY"
    FIXED = "FIXED"


class Service(Base):
    __tablename__ = "Service"
    
    id = Column(String, primary_key=True)
    
    userId = Column(String, ForeignKey("User.id"))
    name = Column(String)
    desc = Column(String)
    serviceimg = Column(String)
    experience = Column(Integer, nullable=True)
    altPhone = Column(String, nullable=True)
    coverImg = Column(String, nullable=True)
    mainimg = Column(String, nullable=True)
    
    categoryId = Column(String, ForeignKey("Category.id"), nullable=True)
    
    subCategoryIds = Column(ARRAY(String))
    priceType = Column(Enum(PriceTypeEnum), default=PriceTypeEnum.FIXED)
    price = Column(Float, default=0)
    
    # Address
    addressLine1 = Column(String, nullable=True)
    addressLine2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    
    # Location
    latitude = Column(Numeric, nullable=True)
    longitude = Column(Numeric, nullable=True)
    radiusKm = Column(Integer, default=10)
    
    # Availability
    workingDays = Column(ARRAY(String))
    openTime = Column(String, nullable=True)
    closeTime = Column(String, nullable=True)
    
    # Details
    rating = Column(Float, default=5.0)
    loc = Column(String, nullable=True)
    isVerified = Column(Boolean, default=False)
    gallery = Column(ARRAY(String))
    
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="services")
    category = relationship("Category", back_populates="services")
    bookings = relationship("Booking", back_populates="service")
