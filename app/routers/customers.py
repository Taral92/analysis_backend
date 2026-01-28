"""
Customer Analytics API endpoints.
Routes for customer segmentation, lifetime value, demographics.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services import AnalyticsService
from app.schemas.analytics import CustomerSegment, GeographicData
from app.utils.cache import cached

router = APIRouter(prefix="/customers", tags=["Customer Analytics"])


@router.get("/segmentation")
@cached(ttl=600, key_prefix="customers")
async def get_customer_segmentation(db: Session = Depends(get_db)):
    """
    Segment customers by behavior and value.
    
    Returns:
    - High-value customers (top spenders)
    - Frequent buyers (most orders)
    - Cash-only vs Online-only users
    - Total customer count
    
    Use for:
    - Targeted marketing campaigns
    - Loyalty programs
    - Payment method promotions
    """
    service = AnalyticsService(db)
    return service.get_customer_segmentation()


@router.get("/geographic")
@cached(ttl=600, key_prefix="customers")
async def get_geographic_analysis(db: Session = Depends(get_db)):
    """
    Analyze customers and orders by location.
    
    Returns top locations by:
    - Order count
    - Revenue
    - Customer count
    
    Breakdown by:
    - City
    - State
    - Pincode
    
    Use for:
    - Delivery zone optimization
    - Regional marketing
    - Warehouse placement decisions
    """
    service = AnalyticsService(db)
    return service.get_geographic_analysis()


@router.get("/lifetime-value")
@cached(ttl=600, key_prefix="customers")
async def get_customer_lifetime_value(
    limit: int = Query(50, description="Number of top customers to return"),
    db: Session = Depends(get_db)
):
    """
    Calculate and predict customer lifetime value (CLV).
    
    Returns top customers ranked by:
    - Total spent
    - Order frequency
    - Predicted annual value
    
    Helps identify:
    - VIP customers for special treatment
    - Retention opportunities
    - Upsell potential
    """
    from app.services import MLService
    
    ml_service = MLService(db)
    return ml_service.get_customer_lifetime_value_prediction()[:limit]


@router.get("/demographics")
@cached(ttl=600, key_prefix="customers")
async def get_customer_demographics(db: Session = Depends(get_db)):
    """
    Analyze customer demographics.
    
    Returns:
    - Gender distribution
    - Age groups (if DOB available)
    - Worker vs Regular user split
    - Verification status
    """
    from app.models import User
    from sqlalchemy import func
    from app.utils.helpers import get_date_range
    
    # Gender distribution
    gender_stats = db.query(
        User.gender,
        func.count(User.id).label('count')
    ).group_by(User.gender).all()
    
    # User types
    user_types = db.query(
        func.count(func.nullif(User.isWorker == True, False)).label('workers'),
        func.count(func.nullif(User.isWorker == False, False)).label('customers'),
        func.count(func.nullif(User.isVerified == True, False)).label('verified'),
        func.count(User.id).label('total')
    ).first()
    
    return {
        "gender_distribution": [
            {"gender": row.gender.value if row.gender else "Not Specified", "count": row.count}
            for row in gender_stats
        ],
        "user_types": {
            "workers": user_types.workers,
            "customers": user_types.customers,
            "verified_users": user_types.verified,
            "total_users": user_types.total
        }
    }


@router.get("/new-vs-returning")
@cached(ttl=600, key_prefix="customers")
async def get_new_vs_returning_customers(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Analyze new vs returning customers.
    
    Returns:
    - New customers (first order in period)
    - Returning customers (2+ orders)
    - Retention rate
    """
    from app.models import Order, User
    from sqlalchemy import func, and_
    from app.utils.helpers import get_date_range
    
    start_date, end_date = get_date_range(days)
    
    # Get customers with their first order date
    first_orders = db.query(
        Order.userId,
        func.min(Order.createdAt).label('first_order')
    ).group_by(Order.userId).subquery()
    
    # New customers (first order in this period)
    new_customers = db.query(
        func.count(func.distinct(Order.userId))
    ).join(
        first_orders,
        Order.userId == first_orders.c.userId
    ).filter(
        first_orders.c.first_order.between(start_date, end_date)
    ).scalar()
    
    # Returning customers (ordered before AND during this period)
    returning_customers = db.query(
        func.count(func.distinct(Order.userId))
    ).join(
        first_orders,
        Order.userId == first_orders.c.userId
    ).filter(
        Order.createdAt.between(start_date, end_date),
        first_orders.c.first_order < start_date
    ).scalar()
    
    total = new_customers + returning_customers
    
    return {
        "new_customers": new_customers,
        "returning_customers": returning_customers,
        "total_customers": total,
        "retention_rate": round((returning_customers / total * 100), 2) if total > 0 else 0
    }
