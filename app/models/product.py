"""
Product model - products for sale.
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Enum, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum


class StockStatusEnum(str, enum.Enum):
    IN_STOCK = "IN_STOCK"
    ON_DEMAND = "ON_DEMAND"


class UnitTypeEnum(str, enum.Enum):
    PIECE = "PIECE"
    KG = "KG"
    BOX = "BOX"
    LITER = "LITER"


class DeliveryTypeEnum(str, enum.Enum):
    PICKUP = "PICKUP"
    DELIVERY = "DELIVERY"


class Product(Base):
    __tablename__ = "Product"
    
    id = Column(String, primary_key=True)
    userId = Column(String, ForeignKey("User.id"))
    
    name = Column(String)
    desc = Column(String)
    
    categoryId = Column(String, ForeignKey("Category.id"), nullable=True)
    
    productImage = Column(String)
    gallery = Column(ARRAY(String))
    price = Column(Float)
    moq = Column(Integer)  # Minimum Order Quantity
    
    stockStatus = Column(Enum(StockStatusEnum), default=StockStatusEnum.IN_STOCK)
    unit = Column(Enum(UnitTypeEnum), default=UnitTypeEnum.PIECE)
    deliveryType = Column(Enum(DeliveryTypeEnum), default=DeliveryTypeEnum.DELIVERY)
    
    isVerified = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="products")
    category = relationship("Category", back_populates="products")
    orders = relationship("Order", back_populates="product")
