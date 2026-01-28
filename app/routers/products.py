"""
Product Analytics API endpoints.
Routes for best sellers, category performance, stock alerts.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services import AnalyticsService
from app.schemas.analytics import ProductPerformance, CategoryPerformance
from app.utils.cache import cached

router = APIRouter(prefix="/products", tags=["Product Analytics"])


@router.get("/best-sellers", response_model=List[ProductPerformance])
@cached(ttl=300, key_prefix="products")
async def get_best_sellers(
    limit: int = Query(20, description="Number of products to return"),
    db: Session = Depends(get_db)
):
    """
    Get top-selling products.
    
    Ranked by:
    - Order count
    - Total quantity sold
    - Total revenue generated
    
    Use for:
    - Inventory prioritization
    - Marketing focus
    - Stock planning
    """
    service = AnalyticsService(db)
    return service.get_best_selling_products(limit)


@router.get("/category-performance", response_model=List[CategoryPerformance])
@cached(ttl=600, key_prefix="products")
async def get_category_performance(db: Session = Depends(get_db)):
    """
    Analyze performance by product category.
    
    Returns:
    - Number of products per category
    - Order count per category
    - Total revenue per category
    
    Helps identify:
    - Most profitable categories
    - Underperforming categories
    - Expansion opportunities
    """
    from app.models import Product, Order, Category
    from sqlalchemy import func
    from app.utils.helpers import get_date_range, round_currency
    
    start_date, end_date = get_date_range(30)
    
    results = db.query(
        Category.id,
        Category.name,
        func.count(func.distinct(Product.id)).label('product_count'),
        func.count(Order.id).label('order_count'),
        func.sum(Order.totalPrice).label('total_revenue')
    ).join(
        Product, Category.id == Product.categoryId
    ).join(
        Order, Product.id == Order.productId
    ).filter(
        Order.createdAt.between(start_date, end_date)
    ).group_by(
        Category.id, Category.name
    ).order_by(func.sum(Order.totalPrice).desc()).all()
    
    return [
        {
            "category_id": row.id,
            "category_name": row.name,
            "product_count": row.product_count,
            "order_count": row.order_count,
            "total_revenue": round_currency(row.total_revenue or 0)
        }
        for row in results
    ]


@router.get("/stock-alerts")
@cached(ttl=300, key_prefix="products")
async def get_stock_alerts(db: Session = Depends(get_db)):
    """
    Get products that need restocking based on demand.
    
    Uses ML to predict:
    - Days until stockout
    - Recommended restock quantity
    
    Returns only products with high urgency (< 7 days until stockout).
    """
    from app.services import MLService
    
    ml_service = MLService(db)
    return ml_service.predict_restock_needs()


@router.get("/price-performance")
@cached(ttl=600, key_prefix="products")
async def get_price_performance(db: Session = Depends(get_db)):
    """
    Analyze which price ranges perform best.
    
    Groups products by price range and shows:
    - Order count per range
    - Revenue per range
    - Average order value
    
    Helps with pricing strategy optimization.
    """
    from app.models import Product, Order
    from sqlalchemy import func, case
    from app.utils.helpers import get_date_range, round_currency
    
    start_date, end_date = get_date_range(30)
    
    # Define price ranges
    results = db.query(
        case(
            (Product.price < 500, "Under ₹500"),
            (Product.price < 1000, "₹500-₹1000"),
            (Product.price < 2000, "₹1000-₹2000"),
            (Product.price < 5000, "₹2000-₹5000"),
            else_="Above ₹5000"
        ).label('price_range'),
        func.count(Order.id).label('order_count'),
        func.sum(Order.totalPrice).label('total_revenue'),
        func.avg(Order.totalPrice).label('avg_order_value')
    ).join(
        Order, Product.id == Order.productId
    ).filter(
        Order.createdAt.between(start_date, end_date)
    ).group_by('price_range').all()
    
    return [
        {
            "price_range": row.price_range,
            "order_count": row.order_count,
            "total_revenue": round_currency(row.total_revenue or 0),
            "avg_order_value": round_currency(row.avg_order_value or 0)
        }
        for row in results
    ]


@router.get("/trending")
@cached(ttl=300, key_prefix="products")
async def get_trending_products(
    days: int = Query(7, description="Compare with this many days ago"),
    db: Session = Depends(get_db)
):
    """
    Identify trending products (gaining popularity).
    
    Compares current period vs previous period to find:
    - Products with increasing order velocity
    - Emerging bestsellers
    - Seasonal trends
    """
    from app.models import Product, Order
    from sqlalchemy import func
    from app.utils.helpers import get_date_range, calculate_growth_rate, round_currency
    from datetime import datetime, timedelta
    
    # Current period
    current_end = datetime.utcnow()
    current_start = current_end - timedelta(days=days)
    
    # Previous period
    previous_end = current_start
    previous_start = previous_end - timedelta(days=days)
    
    # Current period orders
    current_results = db.query(
        Order.productId,
        Product.name,
        func.count(Order.id).label('count')
    ).join(
        Product, Order.productId == Product.id
    ).filter(
        Order.createdAt.between(current_start, current_end)
    ).group_by(Order.productId, Product.name).all()
    
    # Previous period orders
    previous_results = db.query(
        Order.productId,
        func.count(Order.id).label('count')
    ).filter(
        Order.createdAt.between(previous_start, previous_end)
    ).group_by(Order.productId).all()
    
    previous_dict = {row.productId: row.count for row in previous_results}
    
    # Calculate growth
    trending = []
    for row in current_results:
        previous_count = previous_dict.get(row.productId, 0)
        growth = calculate_growth_rate(row.count, previous_count)
        
        if growth > 20:  # Only show products with >20% growth
            trending.append({
                "product_id": row.productId,
                "product_name": row.name,
                "current_orders": row.count,
                "previous_orders": previous_count,
                "growth_rate": round(growth, 2)
            })
    
    # Sort by growth rate
    trending.sort(key=lambda x: x['growth_rate'], reverse=True)
    
    return trending[:20]  # Top 20 trending
