"""
Category model - for products and services.
"""
from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class CategoryTypeEnum(str, enum.Enum):
    SERVICE = "SERVICE"
    PRODUCT = "PRODUCT"
    BOTH = "BOTH"


class Category(Base):
    __tablename__ = "Category"
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    type = Column(Enum(CategoryTypeEnum), default=CategoryTypeEnum.BOTH)
    
    # Relationships
    services = relationship("Service", back_populates="category")
    products = relationship("Product", back_populates="category")
