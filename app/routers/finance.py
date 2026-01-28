"""
Financial Analytics API endpoints.
Routes for cash vs online payments, revenue analysis.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.services import AnalyticsService
from app.schemas.analytics import PaymentBreakdown, PaymentTrendsResponse, HourlyPaymentData
from app.utils.cache import cached

router = APIRouter(prefix="/finance", tags=["Financial Analytics"])


@router.get("/overview", response_model=PaymentBreakdown)
@cached(ttl=300, key_prefix="finance")
async def get_payment_overview(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get complete payment breakdown - Cash vs Online.
    
    Returns:
    - Total revenue
    - Cash revenue & percentage
    - Online revenue & percentage
    - Failed payments (lost revenue)
    - Refunded amounts
    - Pending COD payments
    """
    service = AnalyticsService(db)
    
    # Parse dates if provided
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    return service.get_payment_overview(start, end)


@router.get("/trends", response_model=PaymentTrendsResponse)
@cached(ttl=300, key_prefix="finance")
async def get_payment_trends(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get daily payment trends - Cash vs Online over time.
    
    Shows how payment preferences change day by day.
    Useful for tracking online payment adoption.
    """
    service = AnalyticsService(db)
    return service.get_payment_trends(days)


@router.get("/hourly-patterns", response_model=list[HourlyPaymentData])
@cached(ttl=300, key_prefix="finance")
async def get_hourly_payment_patterns(db: Session = Depends(get_db)):
    """
    Analyze which hours prefer cash vs online payments.
    
    Identifies:
    - Peak hours for cash payments
    - Peak hours for online payments
    - Times to promote online payment incentives
    """
    service = AnalyticsService(db)
    return service.get_hourly_payment_patterns()


@router.get("/revenue-summary")
@cached(ttl=300, key_prefix="finance")
async def get_revenue_summary(
    days: int = Query(30, description="Number of days"),
    db: Session = Depends(get_db)
):
    """
    Complete revenue summary with insights.
    
    Returns:
    - Total revenue
    - Revenue by payment method
    - Average order value
    - Revenue growth rate
    """
    service = AnalyticsService(db)
    
    payment_data = service.get_payment_overview()
    velocity = service.get_order_velocity()
    
    return {
        "payment_breakdown": payment_data,
        "growth_metrics": velocity,
        "insights": {
            "online_adoption_rate": payment_data['online_percentage'],
            "cash_dependency": payment_data['cash_percentage'],
            "revenue_at_risk": payment_data['failed_payments_loss']
        }
    }
