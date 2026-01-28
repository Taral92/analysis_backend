"""
Order model - main table for product orders and analytics.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum


class OrderStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"


class PaymentStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class TimelineEnum(str, enum.Enum):
    IMMEDIATE = "IMMEDIATE"
    IN_2_DAYS = "IN_2_DAYS"
    TWO_TO_FIVE_DAYS = "TWO_TO_FIVE_DAYS"


class UnitTypeEnum(str, enum.Enum):
    PIECE = "PIECE"
    KG = "KG"
    BOX = "BOX"
    LITER = "LITER"


class Order(Base):
    __tablename__ = "Order"
    
    id = Column(String, primary_key=True)
    
    # Relations
    userId = Column(String, ForeignKey("User.id"))
    productId = Column(String, ForeignKey("Product.id"))
    addressId = Column(String, ForeignKey("Address.id"), nullable=True)
    
    # Order details
    quantity = Column(Integer)
    unit = Column(Enum(UnitTypeEnum))
    totalPrice = Column(Float)
    
    # Status & Payment
    status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.PENDING)
    timeline = Column(Enum(TimelineEnum), default=TimelineEnum.IMMEDIATE)
    paymentStatus = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.PENDING)
    
    # Extras
    specialInstructions = Column(String, nullable=True)
    trackingId = Column(String, nullable=True)
    
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    address = relationship("Address", back_populates="orders")
