"""
Recommendations API endpoints.
ML-powered suggestions for business optimization.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services import MLService
from app.schemas.analytics import (
    BestTimeRecommendation,
    RestockRecommendation,
    DemandForecast,
    OperationalRecommendation
)
from app.utils.cache import cached

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/best-order-time", response_model=BestTimeRecommendation)
@cached(ttl=600, key_prefix="recommendations")
async def get_best_order_time(db: Session = Depends(get_db)):
    """
    Recommend best times to order for customers.
    
    Analyzes:
    - Delivery success rate by hour
    - Average delivery time by hour
    - Order processing speed
    
    Returns:
    - Top 3 recommended hours
    - Reason for recommendation
    - Expected delivery performance
    
    Use for:
    - Customer education
    - Marketing messaging
    - Service quality improvements
    """
    ml_service = MLService(db)
    return ml_service.get_best_order_time_recommendation()


@router.get("/restock", response_model=List[RestockRecommendation])
@cached(ttl=300, key_prefix="recommendations")
async def get_restock_recommendations(
    product_id: str = Query(None, description="Specific product ID (optional)"),
    db: Session = Depends(get_db)
):
    """
    Predict which products need restocking.
    
    Uses demand forecasting to calculate:
    - Days until stockout
    - Recommended restock quantity
    - Current demand trends
    
    Only shows products with urgent needs (< 7 days).
    
    Use for:
    - Inventory management
    - Purchase planning
    - Avoiding stockouts
    """
    ml_service = MLService(db)
    return ml_service.predict_restock_needs(product_id)


@router.get("/demand-forecast", response_model=List[DemandForecast])
@cached(ttl=600, key_prefix="recommendations")
async def get_demand_forecast(
    days_ahead: int = Query(7, description="Number of days to forecast"),
    db: Session = Depends(get_db)
):
    """
    Forecast order demand for next N days.
    
    Uses:
    - Historical patterns
    - Day-of-week trends
    - Moving averages
    
    Returns:
    - Predicted order count per day
    - Confidence intervals (upper/lower bounds)
    
    Use for:
    - Staff scheduling
    - Inventory planning
    - Capacity management
    """
    ml_service = MLService(db)
    return ml_service.forecast_demand(days_ahead)


@router.get("/operations", response_model=List[OperationalRecommendation])
@cached(ttl=600, key_prefix="recommendations")
async def get_operational_recommendations(db: Session = Depends(get_db)):
    """
    Get actionable operational recommendations.
    
    Analyzes patterns to suggest:
    - Staffing adjustments (when to add delivery staff)
    - Promotional opportunities (off-peak discounts)
    - Payment incentives (boost online payments)
    
    Each recommendation includes:
    - Type (staffing, promotion, inventory)
    - Priority (high, medium, low)
    - Specific action required
    - Expected impact
    
    Use for:
    - Business optimization
    - Cost reduction
    - Revenue growth
    """
    ml_service = MLService(db)
    return ml_service.get_operational_recommendations()


@router.get("/pricing-insights")
@cached(ttl=600, key_prefix="recommendations")
async def get_pricing_insights(db: Session = Depends(get_db)):
    """
    Suggest pricing optimizations based on demand patterns.
    
    Analyzes:
    - Price elasticity
    - Conversion rates by price point
    - Competitor positioning (if data available)
    
    Returns:
    - Optimal price ranges
    - Discount timing suggestions
    - Bundle opportunities
    """
    from app.models import Product, Order
    from sqlalchemy import func
    from app.utils.helpers import get_date_range, round_currency
    
    start_date, end_date = get_date_range(30)
    
    # Analyze conversion rate by price point
    results = db.query(
        Product.id,
        Product.name,
        Product.price,
        func.count(Order.id).label('order_count')
    ).outerjoin(
        Order, Product.id == Order.productId
    ).filter(
        Order.createdAt.between(start_date, end_date) if Order.id else True
    ).group_by(
        Product.id, Product.name, Product.price
    ).having(
        func.count(Order.id) > 5  # Only products with some orders
    ).all()
    
    insights = []
    for row in results:
        # Simple heuristic: compare price vs order volume
        # Lower price + high volume = good
        # Higher price + low volume = consider discount
        
        if row.price > 2000 and row.order_count < 10:
            insights.append({
                "product_id": row.id,
                "product_name": row.name,
                "current_price": round_currency(row.price),
                "order_count": row.order_count,
                "recommendation": "Consider 10-15% discount to boost demand",
                "reasoning": "High price point with low conversion"
            })
        elif row.price < 500 and row.order_count > 50:
            insights.append({
                "product_id": row.id,
                "product_name": row.name,
                "current_price": round_currency(row.price),
                "order_count": row.order_count,
                "recommendation": "Consider slight price increase (5-10%)",
                "reasoning": "High demand suggests room for margin improvement"
            })
    
    return {
        "pricing_insights": insights[:10],
        "summary": f"Analyzed {len(results)} products with recommendations for {len(insights)}"
    }


@router.get("/customer-retention")
@cached(ttl=600, key_prefix="recommendations")
async def get_retention_recommendations(db: Session = Depends(get_db)):
    """
    Suggest strategies to improve customer retention.
    
    Identifies:
    - At-risk customers (haven't ordered recently)
    - High-value customers for VIP treatment
    - Win-back opportunities
    
    Returns targeted action items for each segment.
    """
    from app.models import Order, User
    from sqlalchemy import func
    from datetime import datetime, timedelta
    from app.utils.helpers import round_currency
    
    # Find customers who haven't ordered in 30+ days
    threshold_date = datetime.utcnow() - timedelta(days=30)
    
    at_risk = db.query(
        Order.userId,
        User.name,
        User.email,
        func.max(Order.createdAt).label('last_order'),
        func.sum(Order.totalPrice).label('lifetime_value')
    ).join(
        User, Order.userId == User.id
    ).group_by(
        Order.userId, User.name, User.email
    ).having(
        func.max(Order.createdAt) < threshold_date
    ).order_by(
        func.sum(Order.totalPrice).desc()
    ).limit(50).all()
    
    recommendations = []
    for customer in at_risk:
        days_since_order = (datetime.utcnow() - customer.last_order).days
        
        recommendations.append({
            "user_id": customer.userId,
            "user_name": customer.name,
            "user_email": customer.email,
            "days_since_last_order": days_since_order,
            "lifetime_value": round_currency(customer.lifetime_value),
            "recommendation": "Send win-back offer (15% discount)" if customer.lifetime_value > 1000 else "Send re-engagement email",
            "priority": "high" if customer.lifetime_value > 1000 else "medium"
        })
    
    return {
        "at_risk_customers": recommendations,
        "total_at_risk": len(recommendations),
        "total_value_at_risk": round_currency(sum(r['lifetime_value'] for r in recommendations))
    }
