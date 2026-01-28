"""
Geographic Analytics API endpoints.
Routes for location-based insights, delivery zones, heatmaps.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.cache import cached

router = APIRouter(prefix="/geography", tags=["Geographic Analytics"])


@router.get("/heatmap")
@cached(ttl=600, key_prefix="geography")
async def get_order_heatmap(db: Session = Depends(get_db)):
    """
    Generate geographic heatmap data for orders.
    
    Returns order density by:
    - City
    - Pincode
    - State
    
    Use for:
    - Visualizing demand hotspots
    - Delivery zone planning
    - Warehouse location decisions
    """
    from app.models import Order, Address
    from sqlalchemy import func
    from app.utils.helpers import get_date_range
    
    start_date, end_date = get_date_range(30)
    
    # City-level heatmap
    city_results = db.query(
        Address.city,
        Address.state,
        func.count(Order.id).label('order_count'),
        func.sum(Order.totalPrice).label('revenue')
    ).join(
        Order, Address.id == Order.addressId
    ).filter(
        Order.createdAt.between(start_date, end_date)
    ).group_by(
        Address.city, Address.state
    ).order_by(
        func.count(Order.id).desc()
    ).limit(100).all()
    
    # Pincode-level heatmap
    pincode_results = db.query(
        Address.pincode,
        Address.city,
        func.count(Order.id).label('order_count')
    ).join(
        Order, Address.id == Order.addressId
    ).filter(
        Order.createdAt.between(start_date, end_date)
    ).group_by(
        Address.pincode, Address.city
    ).order_by(
        func.count(Order.id).desc()
    ).limit(100).all()
    
    return {
        "city_heatmap": [
            {
                "city": row.city,
                "state": row.state,
                "order_count": row.order_count,
                "revenue": round(row.revenue or 0, 2)
            }
            for row in city_results
        ],
        "pincode_heatmap": [
            {
                "pincode": row.pincode,
                "city": row.city,
                "order_count": row.order_count
            }
            for row in pincode_results
        ]
    }


@router.get("/delivery-zones")
@cached(ttl=600, key_prefix="geography")
async def get_delivery_zone_analysis(db: Session = Depends(get_db)):
    """
    Analyze delivery zones for optimization.
    
    Returns:
    - High-demand zones (prioritize resources)
    - Low-demand zones (consider discontinuing)
    - Growth opportunities (emerging areas)
    
    Use for:
    - Delivery route optimization
    - Resource allocation
    - Expansion planning
    """
    from app.models import Order, Address
    from app.models.order import OrderStatusEnum
    from sqlalchemy import func
    from app.utils.helpers import get_date_range, calculate_percentage
    
    start_date, end_date = get_date_range(30)
    
    results = db.query(
        Address.city,
        Address.pincode,
        func.count(Order.id).label('total_orders'),
        func.count(
            func.nullif(Order.status == OrderStatusEnum.DELIVERED, False)
        ).label('delivered_orders'),
        func.avg(
            func.extract('epoch', Order.updatedAt - Order.createdAt) / 3600
        ).label('avg_delivery_hours')
    ).join(
        Order, Address.id == Order.addressId
    ).filter(
        Order.createdAt.between(start_date, end_date)
    ).group_by(
        Address.city, Address.pincode
    ).having(
        func.count(Order.id) >= 5  # Only zones with at least 5 orders
    ).all()
    
    zones = []
    for row in results:
        delivery_success_rate = calculate_percentage(row.delivered_orders, row.total_orders)
        
        # Classify zones
        if row.total_orders > 50:
            zone_type = "high_demand"
        elif row.total_orders > 20:
            zone_type = "medium_demand"
        else:
            zone_type = "low_demand"
        
        zones.append({
            "city": row.city,
            "pincode": row.pincode,
            "total_orders": row.total_orders,
            "delivered_orders": row.delivered_orders,
            "delivery_success_rate": round(delivery_success_rate, 2),
            "avg_delivery_hours": round(row.avg_delivery_hours or 0, 2),
            "zone_type": zone_type
        })
    
    return {
        "delivery_zones": zones,
        "summary": {
            "high_demand_zones": len([z for z in zones if z['zone_type'] == 'high_demand']),
            "medium_demand_zones": len([z for z in zones if z['zone_type'] == 'medium_demand']),
            "low_demand_zones": len([z for z in zones if z['zone_type'] == 'low_demand'])
        }
    }


@router.get("/state-performance")
@cached(ttl=600, key_prefix="geography")
async def get_state_performance(db: Session = Depends(get_db)):
    """
    Analyze performance by state.
    
    Returns:
    - Order count per state
    - Revenue per state
    - Average order value per state
    - Customer count per state
    
    Use for:
    - Regional marketing
    - State-level expansion decisions
    - Competitive analysis
    """
    from app.models import Order, Address
    from sqlalchemy import func
    from app.utils.helpers import get_date_range, round_currency
    
    start_date, end_date = get_date_range(30)
    
    results = db.query(
        Address.state,
        func.count(Order.id).label('order_count'),
        func.sum(Order.totalPrice).label('total_revenue'),
        func.avg(Order.totalPrice).label('avg_order_value'),
        func.count(func.distinct(Order.userId)).label('customer_count')
    ).join(
        Order, Address.id == Order.addressId
    ).filter(
        Order.createdAt.between(start_date, end_date)
    ).group_by(
        Address.state
    ).order_by(
        func.sum(Order.totalPrice).desc()
    ).all()
    
    return [
        {
            "state": row.state,
            "order_count": row.order_count,
            "total_revenue": round_currency(row.total_revenue or 0),
            "avg_order_value": round_currency(row.avg_order_value or 0),
            "customer_count": row.customer_count
        }
        for row in results
    ]


@router.get("/distance-analysis")
@cached(ttl=600, key_prefix="geography")
async def get_distance_analysis(db: Session = Depends(get_db)):
    """
    Analyze delivery distance patterns (if coordinates available).
    
    Shows:
    - Average delivery distance
    - Distance vs delivery time correlation
    - Optimal service radius
    
    Note: Requires latitude/longitude data in Service model.
    """
    from app.models import Service
    from sqlalchemy import func
    
    # Count services with location data
    services_with_location = db.query(
        func.count(Service.id)
    ).filter(
        Service.latitude.isnot(None),
        Service.longitude.isnot(None)
    ).scalar()
    
    # Get radius distribution
    radius_stats = db.query(
        Service.radiusKm,
        func.count(Service.id).label('service_count')
    ).filter(
        Service.radiusKm.isnot(None)
    ).group_by(
        Service.radiusKm
    ).all()
    
    return {
        "services_with_location": services_with_location,
        "radius_distribution": [
            {
                "radius_km": row.radiusKm,
                "service_count": row.service_count
            }
            for row in radius_stats
        ],
        "note": "Full distance analysis requires geocoding order addresses"
    }
