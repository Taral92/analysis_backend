"""
User model - represents customers and workers.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum


class GenderEnum(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class PayoutMethodEnum(str, enum.Enum):
    BANK = "BANK"
    UPI = "UPI"


class User(Base):
    __tablename__ = "User"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    shopName = Column(String, nullable=True)
    phone = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=True)
    emailVerified = Column(DateTime, nullable=True)
    image = Column(String, nullable=True)
    
    role = Column(String, default="USER")
    profileImage = Column(String, nullable=True)
    
    gender = Column(Enum(GenderEnum), nullable=True)
    dob = Column(DateTime, nullable=True)
    preferredLanguage = Column(String, default="English")
    
    isPhoneVerified = Column(Boolean, default=False)
    isWorker = Column(Boolean, default=False)
    isWebsite = Column(Boolean, default=True)
    rejectionReason = Column(String, nullable=True)
    
    instagramUrl = Column(String, nullable=True)
    facebookUrl = Column(String, nullable=True)
    websiteUrl = Column(String, nullable=True)
    youtubeUrl = Column(String, nullable=True)
    isVerified = Column(Boolean, default=False)
    
    # Banking
    bankAccountHolder = Column(String, nullable=True)
    bankAccountNumber = Column(String, nullable=True)
    bankIfsc = Column(String, nullable=True)
    bankName = Column(String, nullable=True)
    upiId = Column(String, nullable=True)
    preferredPayoutMethod = Column(Enum(PayoutMethodEnum), default=PayoutMethodEnum.BANK)
    
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    addresses = relationship("Address", back_populates="user")
    orders = relationship("Order", back_populates="user")
    bookings = relationship("Booking", back_populates="user")
    products = relationship("Product", back_populates="user")
    services = relationship("Service", back_populates="user")
