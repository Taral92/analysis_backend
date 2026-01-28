"""
Analytics service - Complex business logic for data analysis.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case, and_, or_
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from app.models import Order, Booking, User, Product, Service, Address
from app.models.order import OrderStatusEnum, PaymentStatusEnum
from app.utils.helpers import (
    get_date_range, 
    calculate_growth_rate, 
    calculate_percentage,
    extract_hour,
    extract_day_of_week,
    round_currency,
    safe_divide
)
import pandas as pd


class AnalyticsService:
    """Service class for analytics operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ===== FINANCIAL ANALYTICS =====
    
    def get_payment_overview(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        Get complete payment breakdown - Cash vs Online.
        
        Since PaymentMode is not in Order table, we infer:
        - PAID = Online payment
        - PENDING = Cash on Delivery (COD)
        """
        if not start_date or not end_date:
            start_date, end_date = get_date_range(30)
        
        # Total revenue
        total_revenue = self.db.query(
            func.coalesce(func.sum(Order.totalPrice), 0)
        ).filter(
            Order.createdAt.between(start_date, end_date),
            Order.status != OrderStatusEnum.CANCELLED
        ).scalar()
        
        # Online revenue (PAID status)
        online_revenue = self.db.query(
            func.coalesce(func.sum(Order.totalPrice), 0)
        ).filter(
            Order.createdAt.between(start_date, end_date),
            Order.paymentStatus == PaymentStatusEnum.PAID,
            Order.status != OrderStatusEnum.CANCELLED
        ).scalar()
        
        # Cash revenue (PENDING status - COD)
        cash_revenue = self.db.query(
            func.coalesce(func.sum(Order.totalPrice), 0)
        ).filter(
            Order.createdAt.between(start_date, end_date),
            Order.paymentStatus == PaymentStatusEnum.PENDING,
            Order.status != OrderStatusEnum.CANCELLED
        ).scalar()
        
        # Failed payments
        failed_payments = self.db.query(
            func.coalesce(func.sum(Order.totalPrice), 0)
        ).filter(
            Order.createdAt.between(start_date, end_date),
            Order.paymentStatus == PaymentStatusEnum.FAILED
        ).scalar()
        
        # Refunded amount
        refunded_amount = self.db.query(
            func.coalesce(func.sum(Order.totalPrice), 0)
        ).filter(
            Order.createdAt.between(start_date, end_date),
            Order.paymentStatus == PaymentStatusEnum.REFUNDED
        ).scalar()
        
        return {
            "total_revenue": round_currency(total_revenue),
            "cash_revenue": round_currency(cash_revenue),
            "online_revenue": round_currency(online_revenue),
            "cash_percentage": round_currency(calculate_percentage(cash_revenue, total_revenue)),
            "online_percentage": round_currency(calculate_percentage(online_revenue, total_revenue)),
            "failed_payments_loss": round_currency(failed_payments),
            "refunded_amount": round_currency(refunded_amount),
            "pending_cod": round_currency(cash_revenue)
        }
    
    def get_payment_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get daily payment trends - Cash vs Online."""
        start_date, end_date = get_date_range(days)
        
        # Query daily breakdown
        results = self.db.query(
            func.date(Order.createdAt).label('date'),
            func.sum(
                case((Order.paymentStatus == PaymentStatusEnum.PAID, Order.totalPrice), else_=0)
            ).label('online_amount'),
            func.sum(
                case((Order.paymentStatus == PaymentStatusEnum.PENDING, Order.totalPrice), else_=0)
            ).label('cash_amount'),
            func.sum(Order.totalPrice).label('total_amount')
        ).filter(
            Order.createdAt.between(start_date, end_date),
            Order.status != OrderStatusEnum.CANCELLED
        ).group_by(
            func.date(Order.createdAt)
        ).order_by('date').all()
        
        trends = []
        for row in results:
            trends.append({
                "date": str(row.date),
                "cash_amount": round_currency(row.cash_amount or 0),
                "online_amount": round_currency(row.online_amount or 0),
                "total_amount": round_currency(row.total_amount or 0)
            })
        
        summary = self.get_payment_overview(start_date, end_date)
        
        return {
            "trends": trends,
            "summary": summary
        }
    
    def get_hourly_payment_patterns(self) -> List[Dict[str, Any]]:
        """Analyze which hours prefer cash vs online."""
        start_date, end_date = get_date_range(30)
        
        results = self.db.query(
            extract('hour', Order.createdAt).label('hour'),
            func.count(
                case((Order.paymentStatus == PaymentStatusEnum.PENDING, 1))
            ).label('cash_orders'),
            func.count(
                case((Order.paymentStatus == PaymentStatusEnum.PAID, 1))
            ).label('online_orders'),
            func.sum(
                case((Order.paymentStatus == PaymentStatusEnum.PENDING, Order.totalPrice), else_=0)
            ).label('cash_amount'),
            func.sum(
                case((Order.paymentStatus == PaymentStatusEnum.PAID, Order.totalPrice), else_=0)
            ).label('online_amount')
        ).filter(
            Order.createdAt.between(start_date, end_date),
            Order.status != OrderStatusEnum.CANCELLED
        ).group_by('hour').order_by('hour').all()
        
        hourly_data = []
        for row in results:
            hourly_data.append({
                "hour": int(row.hour),
                "cash_orders": row.cash_orders,
                "online_orders": row.online_orders,
                "cash_amount": round_currency(row.cash_amount or 0),
                "online_amount": round_currency(row.online_amount or 0)
            })
        
        return hourly_data
    
    # ===== ORDER ANALYTICS =====
    
    def get_peak_hours(self, days: int = 30) -> List[Dict[str, Any]]:
        """Analyze peak hours for orders."""
        start_date, end_date = get_date_range(days)
        
        results = self.db.query(
            extract('hour', Order.createdAt).label('hour'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.totalPrice).label('total_revenue'),
            func.avg(Order.totalPrice).label('avg_order_value')
        ).filter(
            Order.createdAt.between(start_date, end_date),
            Order.status != OrderStatusEnum.CANCELLED
        ).group_by('hour').order_by('hour').all()
        
        peak_data = []
        for row in results:
            peak_data.append({
                "hour": int(row.hour),
                "order_count": row.order_count,
                "total_revenue": round_currency(row.total_revenue or 0),
                "avg_order_value": round_currency(row.avg_order_value or 0)
            })
        
        return peak_data
    
    def get_day_of_week_analysis(self, days: int = 30) -> List[Dict[str, Any]]:
        """Analyze orders by day of week."""
        start_date, end_date = get_date_range(days)
        
        # PostgreSQL: day of week (0=Sunday, 1=Monday, etc)
        # We'll convert to Python's convention (0=Monday)
        results = self.db.query(
            extract('dow', Order.createdAt).label('day_number'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.totalPrice).label('total_revenue')
        ).filter(
            Order.createdAt.between(start_date, end_date),
            Order.status != OrderStatusEnum.CANCELLED
        ).group_by('day_number').order_by('day_number').all()
        
        # Day names mapping (PostgreSQL dow: 0=Sunday, 1=Monday...)
        day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        
        day_data = []
        for row in results:
            day_num = int(row.day_number)
            day_data.append({
                "day": day_names[day_num],
                "day_number": day_num,
                "order_count": row.order_count,
                "total_revenue": round_currency(row.total_revenue or 0)
            })
        
        return day_data
    
    def get_order_velocity(self) -> Dict[str, Any]:
        """Calculate order velocity and growth rates."""
        now = datetime.utcnow()
        
        # This week
        week_start = now - timedelta(days=now.weekday())
        this_week_orders = self.db.query(func.count(Order.id)).filter(
            Order.createdAt >= week_start
        ).scalar()
        
        # Last week
        last_week_start = week_start - timedelta(days=7)
        last_week_end = week_start
        last_week_orders = self.db.query(func.count(Order.id)).filter(
            Order.createdAt.between(last_week_start, last_week_end)
        ).scalar()
        
        # This month
        month_start = now.replace(day=1)
        this_month_orders = self.db.query(func.count(Order.id)).filter(
            Order.createdAt >= month_start
        ).scalar()
        
        # Last month
        if month_start.month == 1:
            last_month_start = month_start.replace(year=month_start.year - 1, month=12)
        else:
            last_month_start = month_start.replace(month=month_start.month - 1)
        
        last_month_orders = self.db.query(func.count(Order.id)).filter(
            Order.createdAt.between(last_month_start, month_start)
        ).scalar()
        
        return {
            "weekly": {
                "current": this_week_orders,
                "previous": last_week_orders,
                "growth_rate": round_currency(calculate_growth_rate(this_week_orders, last_week_orders))
            },
            "monthly": {
                "current": this_month_orders,
                "previous": last_month_orders,
                "growth_rate": round_currency(calculate_growth_rate(this_month_orders, last_month_orders))
            }
        }
    
    def get_order_funnel(self) -> Dict[str, Any]:
        """Analyze order status conversion funnel."""
        start_date, end_date = get_date_range(30)
        
        # Count by status
        results = self.db.query(
            Order.status,
            func.count(Order.id).label('count')
        ).filter(
            Order.createdAt.between(start_date, end_date)
        ).group_by(Order.status).all()
        
        status_counts = {row.status.value: row.count for row in results}
        
        total_orders = sum(status_counts.values())
        delivered = status_counts.get('DELIVERED', 0)
        cancelled = status_counts.get('CANCELLED', 0)
        
        return {
            "pending": status_counts.get('PENDING', 0),
            "confirmed": status_counts.get('CONFIRMED', 0),
            "shipped": status_counts.get('SHIPPED', 0),
            "out_for_delivery": status_counts.get('OUT_FOR_DELIVERY', 0),
            "delivered": delivered,
            "cancelled": cancelled,
            "returned": status_counts.get('RETURNED', 0),
            "total_orders": total_orders,
            "conversion_rate": round_currency(calculate_percentage(delivered, total_orders)),
            "cancellation_rate": round_currency(calculate_percentage(cancelled, total_orders))
        }
    
    # ===== CUSTOMER ANALYTICS =====
    
    def get_customer_segmentation(self) -> List[Dict[str, Any]]:
        """Segment customers by behavior and value."""
        start_date, end_date = get_date_range(90)  # Last 3 months
        
        # Get customer data with aggregations
        results = self.db.query(
            Order.userId,
            User.name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.totalPrice).label('total_spent'),
            func.avg(Order.totalPrice).label('avg_order_value'),
            func.count(
                case((Order.paymentStatus == PaymentStatusEnum.PENDING, 1))
            ).label('cash_orders'),
            func.count(
                case((Order.paymentStatus == PaymentStatusEnum.PAID, 1))
            ).label('online_orders')
        ).join(
            User, Order.userId == User.id
        ).filter(
            Order.createdAt.between(start_date, end_date),
            Order.status != OrderStatusEnum.CANCELLED
        ).group_by(Order.userId, User.name).all()
        
        # Segment customers
        high_value = []
        frequent_buyers = []
        cash_only = []
        online_only = []
        
        for row in results:
            customer_data = {
                "user_id": row.userId,
                "name": row.name,
                "order_count": row.order_count,
                "total_spent": round_currency(row.total_spent),
                "avg_order_value": round_currency(row.avg_order_value)
            }
            
            # High value: >$1000 total spent
            if row.total_spent > 1000:
                high_value.append(customer_data)
            
            # Frequent buyers: >10 orders
            if row.order_count > 10:
                frequent_buyers.append(customer_data)
            
            # Cash only
            if row.cash_orders > 0 and row.online_orders == 0:
                cash_only.append(customer_data)
            
            # Online only
            if row.online_orders > 0 and row.cash_orders == 0:
                online_only.append(customer_data)
        
        return {
            "high_value_customers": high_value[:20],  # Top 20
            "frequent_buyers": frequent_buyers[:20],
            "cash_only_users": len(cash_only),
            "online_only_users": len(online_only),
            "total_customers": len(results)
        }
    
    def get_geographic_analysis(self) -> List[Dict[str, Any]]:
        """Analyze orders by geographic location."""
        start_date, end_date = get_date_range(30)
        
        results = self.db.query(
            Address.city,
            Address.state,
            Address.pincode,
            func.count(Order.id).label('order_count'),
            func.sum(Order.totalPrice).label('revenue'),
            func.count(func.distinct(Order.userId)).label('customer_count')
        ).join(
            Order, Address.id == Order.addressId
        ).filter(
            Order.createdAt.between(start_date, end_date),
            Order.status != OrderStatusEnum.CANCELLED
        ).group_by(
            Address.city, Address.state, Address.pincode
        ).order_by(func.count(Order.id).desc()).limit(50).all()
        
        geographic_data = []
        for row in results:
            geographic_data.append({
                "city": row.city,
                "state": row.state,
                "pincode": row.pincode,
                "order_count": row.order_count,
                "revenue": round_currency(row.revenue),
                "customer_count": row.customer_count
            })
        
        return geographic_data
    
    # ===== PRODUCT ANALYTICS =====
    
    def get_best_selling_products(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top-selling products."""
        start_date, end_date = get_date_range(30)
        
        results = self.db.query(
            Product.id,
            Product.name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.quantity).label('total_quantity'),
            func.sum(Order.totalPrice).label('total_revenue'),
            func.avg(Order.totalPrice).label('avg_price')
        ).join(
            Order, Product.id == Order.productId
        ).filter(
            Order.createdAt.between(start_date, end_date),
            Order.status != OrderStatusEnum.CANCELLED
        ).group_by(
            Product.id, Product.name
        ).order_by(func.count(Order.id).desc()).limit(limit).all()
        
        products = []
        for row in results:
            products.append({
                "product_id": row.id,
                "product_name": row.name,
                "order_count": row.order_count,
                "total_quantity": row.total_quantity,
                "total_revenue": round_currency(row.total_revenue),
                "avg_price": round_currency(row.avg_price)
            })
        
        return products
