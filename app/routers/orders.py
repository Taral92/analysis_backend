"""
Order Analytics API endpoints.
Routes for peak hours, order velocity, funnels, etc.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services import AnalyticsService
from app.schemas.analytics import PeakHourData, DayOfWeekData, OrderVelocity, OrderFunnel
from app.utils.cache import cached

router = APIRouter(prefix="/orders", tags=["Order Analytics"])


@router.get("/peak-hours", response_model=List[PeakHourData])
@cached(ttl=300, key_prefix="orders")
async def get_peak_hours(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Analyze peak hours for orders.
    
    Returns hourly breakdown (0-23) showing:
    - Order count per hour
    - Total revenue per hour
    - Average order value per hour
    
    Use this to:
    - Optimize staffing schedules
    - Plan delivery capacity
    - Schedule maintenance during low-traffic hours
    """
    service = AnalyticsService(db)
    return service.get_peak_hours(days)


@router.get("/day-of-week", response_model=List[DayOfWeekData])
@cached(ttl=300, key_prefix="orders")
async def get_day_of_week_analysis(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Analyze orders by day of week.
    
    Shows which days are busiest (Monday-Sunday).
    Helps with:
    - Weekly staffing planning
    - Inventory management
    - Marketing campaign timing
    """
    service = AnalyticsService(db)
    return service.get_day_of_week_analysis(days)


@router.get("/velocity", response_model=dict)
@cached(ttl=300, key_prefix="orders")
async def get_order_velocity(db: Session = Depends(get_db)):
    """
    Calculate order velocity and growth rates.
    
    Returns:
    - Weekly order count (current vs previous)
    - Monthly order count (current vs previous)
    - Growth rates (Week-over-Week, Month-over-Month)
    
    Essential for tracking business growth trends.
    """
    service = AnalyticsService(db)
    return service.get_order_velocity()


@router.get("/funnel", response_model=OrderFunnel)
@cached(ttl=300, key_prefix="orders")
async def get_order_funnel(db: Session = Depends(get_db)):
    """
    Analyze order status conversion funnel.
    
    Shows drop-off at each stage:
    PENDING → CONFIRMED → SHIPPED → OUT_FOR_DELIVERY → DELIVERED
    
    Also tracks:
    - Cancellation rate
    - Return rate
    - Overall conversion rate
    
    Use to identify bottlenecks in the order fulfillment process.
    """
    service = AnalyticsService(db)
    return service.get_order_funnel()


@router.get("/timeline-analysis")
@cached(ttl=300, key_prefix="orders")
async def get_timeline_analysis(db: Session = Depends(get_db)):
    """
    Analyze order preferences by timeline (IMMEDIATE, IN_2_DAYS, etc).
    
    Shows:
    - Percentage of immediate vs scheduled orders
    - Success rate by timeline type
    - Average delivery time by timeline
    """
    from app.models import Order
    from sqlalchemy import func
    
    results = db.query(
        Order.timeline,
        func.count(Order.id).label('count'),
        func.avg(func.extract('epoch', Order.updatedAt - Order.createdAt) / 3600).label('avg_hours')
    ).group_by(Order.timeline).all()
    
    total = sum(r.count for r in results)
    
    timeline_data = []
    for row in results:
        timeline_data.append({
            "timeline": row.timeline.value,
            "order_count": row.count,
            "percentage": round((row.count / total * 100), 2) if total > 0 else 0,
            "avg_completion_hours": round(row.avg_hours or 0, 2)
        })
    
    return {"timeline_breakdown": timeline_data}


@router.get("/status-distribution")
@cached(ttl=300, key_prefix="orders")
async def get_status_distribution(db: Session = Depends(get_db)):
    """
    Current distribution of orders by status.
    
    Real-time snapshot of:
    - How many orders are pending
    - How many are in transit
    - How many are completed
    """
    from app.models import Order
    from sqlalchemy import func
    from app.utils.helpers import get_date_range
    
    start_date, end_date = get_date_range(7)  # Last 7 days
    
    results = db.query(
        Order.status,
        func.count(Order.id).label('count')
    ).filter(
        Order.createdAt.between(start_date, end_date)
    ).group_by(Order.status).all()
    
    return {
        "status_breakdown": [
            {"status": row.status.value, "count": row.count}
            for row in results
        ]
    }
