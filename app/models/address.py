"""
Address model - user addresses for delivery.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Address(Base):
    __tablename__ = "Address"
    
    id = Column(String, primary_key=True)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"))
    
    landmark = Column(String, nullable=True)
    type = Column(String, default="Home")  # Home, Work, Other
    line1 = Column(String)
    line2 = Column(String)
    city = Column(String)
    state = Column(String)
    pincode = Column(String)
    country = Column(String, default="India")
    
    createdAt = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="addresses")
    orders = relationship("Order", back_populates="address")
    bookings = relationship("Booking", back_populates="address")
