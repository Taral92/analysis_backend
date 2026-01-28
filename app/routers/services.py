"""
Service Analytics API endpoints.
Routes for service bookings, provider performance, location demand.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.analytics import ServicePerformance
from app.utils.cache import cached

router = APIRouter(prefix="/services", tags=["Service Analytics"])


@router.get("/popular", response_model=List[ServicePerformance])
@cached(ttl=600, key_prefix="services")
async def get_popular_services(
    limit: int = Query(20, description="Number of services to return"),
    db: Session = Depends(get_db)
):
    """
    Get most popular services by booking count.
    
    Returns:
    - Service name
    - Booking count
    - Average rating
    - Provider information
    
    Use for:
    - Marketing focus
    - Worker recruitment
    - Service expansion planning
    """
    from app.models import Service, Booking, User
    from sqlalchemy import func
    from app.utils.helpers import get_date_range
    
    start_date, end_date = get_date_range(30)
    
    results = db.query(
        Service.id,
        Service.name,
        Service.rating,
        User.name.label('provider_name'),
        func.count(Booking.id).label('booking_count')
    ).join(
        Booking, Service.id == Booking.serviceId
    ).join(
        User, Service.userId == User.id
    ).filter(
        Booking.createdAt.between(start_date, end_date)
    ).group_by(
        Service.id, Service.name, Service.rating, User.name
    ).order_by(
        func.count(Booking.id).desc()
    ).limit(limit).all()
    
    return [
        {
            "service_id": row.id,
            "service_name": row.name,
            "booking_count": row.booking_count,
            "avg_rating": round(row.rating, 2),
            "provider_name": row.provider_name
        }
        for row in results
    ]


@router.get("/provider-performance")
@cached(ttl=600, key_prefix="services")
async def get_provider_performance(db: Session = Depends(get_db)):
    """
    Analyze service provider performance.
    
    Ranks providers by:
    - Number of bookings
    - Average service rating
    - Completion rate
    
    Use for:
    - Provider incentives
    - Quality monitoring
    - Top performer recognition
    """
    from app.models import Service, Booking, User
    from app.models.booking import BookingStatusEnum
    from sqlalchemy import func
    from app.utils.helpers import get_date_range, calculate_percentage
    
    start_date, end_date = get_date_range(60)
    
    results = db.query(
        User.id,
        User.name,
        func.count(Booking.id).label('total_bookings'),
        func.count(
            func.nullif(Booking.status == BookingStatusEnum.COMPLETED, False)
        ).label('completed_bookings'),
        func.avg(Service.rating).label('avg_rating'),
        func.count(func.distinct(Service.id)).label('services_offered')
    ).join(
        Service, User.id == Service.userId
    ).join(
        Booking, Service.id == Booking.serviceId
    ).filter(
        Booking.createdAt.between(start_date, end_date),
        User.isWorker == True
    ).group_by(
        User.id, User.name
    ).order_by(
        func.count(Booking.id).desc()
    ).limit(50).all()
    
    providers = []
    for row in results:
        completion_rate = calculate_percentage(row.completed_bookings, row.total_bookings)
        
        providers.append({
            "provider_id": row.id,
            "provider_name": row.name,
            "total_bookings": row.total_bookings,
            "completed_bookings": row.completed_bookings,
            "completion_rate": round(completion_rate, 2),
            "avg_rating": round(row.avg_rating or 0, 2),
            "services_offered": row.services_offered
        })
    
    return providers


@router.get("/location-demand")
@cached(ttl=600, key_prefix="services")
async def get_location_demand(db: Session = Depends(get_db)):
    """
    Analyze service demand by geographic location.
    
    Shows which areas have:
    - Most service bookings
    - Highest demand
    - Underserved regions
    
    Use for:
    - Worker recruitment targeting
    - Service area expansion
    - Marketing campaigns
    """
    from app.models import Booking, Address
    from sqlalchemy import func
    from app.utils.helpers import get_date_range
    
    start_date, end_date = get_date_range(30)
    
    results = db.query(
        Address.city,
        Address.state,
        Address.pincode,
        func.count(Booking.id).label('booking_count')
    ).join(
        Booking, Address.id == Booking.addressId
    ).filter(
        Booking.createdAt.between(start_date, end_date)
    ).group_by(
        Address.city, Address.state, Address.pincode
    ).order_by(
        func.count(Booking.id).desc()
    ).limit(50).all()
    
    return [
        {
            "city": row.city,
            "state": row.state,
            "pincode": row.pincode,
            "booking_count": row.booking_count
        }
        for row in results
    ]


@router.get("/booking-trends")
@cached(ttl=600, key_prefix="services")
async def get_booking_trends(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Analyze service booking trends over time.
    
    Shows:
    - Daily booking counts
    - Peak booking days
    - Growth trends
    """
    from app.models import Booking
    from sqlalchemy import func
    from app.utils.helpers import get_date_range
    
    start_date, end_date = get_date_range(days)
    
    results = db.query(
        func.date(Booking.createdAt).label('date'),
        func.count(Booking.id).label('booking_count')
    ).filter(
        Booking.createdAt.between(start_date, end_date)
    ).group_by(
        func.date(Booking.createdAt)
    ).order_by('date').all()
    
    return [
        {
            "date": str(row.date),
            "booking_count": row.booking_count
        }
        for row in results
    ]


@router.get("/service-categories")
@cached(ttl=600, key_prefix="services")
async def get_service_category_performance(db: Session = Depends(get_db)):
    """
    Analyze performance by service category.
    
    Returns:
    - Most popular service categories
    - Booking count per category
    - Average ratings per category
    """
    from app.models import Service, Booking, Category
    from sqlalchemy import func
    from app.utils.helpers import get_date_range
    
    start_date, end_date = get_date_range(30)
    
    results = db.query(
        Category.id,
        Category.name,
        func.count(Booking.id).label('booking_count'),
        func.avg(Service.rating).label('avg_rating'),
        func.count(func.distinct(Service.id)).label('service_count')
    ).join(
        Service, Category.id == Service.categoryId
    ).join(
        Booking, Service.id == Booking.serviceId
    ).filter(
        Booking.createdAt.between(start_date, end_date)
    ).group_by(
        Category.id, Category.name
    ).order_by(
        func.count(Booking.id).desc()
    ).all()
    
    return [
        {
            "category_id": row.id,
            "category_name": row.name,
            "booking_count": row.booking_count,
            "avg_rating": round(row.avg_rating or 0, 2),
            "service_count": row.service_count
        }
        for row in results
    ]
