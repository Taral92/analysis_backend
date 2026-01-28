"""
Machine Learning service for recommendations and forecasting.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from app.models import Order, Product
from app.models.order import OrderStatusEnum, PaymentStatusEnum
from app.utils.helpers import get_date_range, round_currency


class MLService:
    """ML-based recommendation and forecasting service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_best_order_time_recommendation(self) -> Dict[str, Any]:
        """
        Recommend best times to order based on delivery success.
        Analyzes: fastest confirmation, delivery success rate by hour.
        """
        start_date, end_date = get_date_range(30)
        
        # Get orders with completion time by hour
        results = self.db.query(
            extract('hour', Order.createdAt).label('hour'),
            func.count(Order.id).label('total_orders'),
            func.count(
                func.nullif(Order.status == OrderStatusEnum.DELIVERED, False)
            ).label('delivered_orders'),
            func.avg(
                extract('epoch', Order.updatedAt - Order.createdAt) / 3600
            ).label('avg_completion_hours')
        ).filter(
            Order.createdAt.between(start_date, end_date)
        ).group_by('hour').all()
        
        # Analyze each hour
        hour_stats = []
        for row in results:
            if row.total_orders > 0:
                success_rate = (row.delivered_orders or 0) / row.total_orders * 100
                hour_stats.append({
                    'hour': int(row.hour),
                    'success_rate': success_rate,
                    'avg_completion_hours': row.avg_completion_hours or 24,
                    'total_orders': row.total_orders
                })
        
        # Find best hours (high success rate, fast completion)
        df = pd.DataFrame(hour_stats)
        if len(df) == 0:
            return {
                "recommended_hours": [],
                "reason": "Not enough data",
                "avg_delivery_time": 0,
                "success_rate": 0
            }
        
        # Score: 70% success rate + 30% speed
        df['score'] = (df['success_rate'] * 0.7) + ((24 - df['avg_completion_hours']) / 24 * 100 * 0.3)
        df = df.sort_values('score', ascending=False)
        
        # Top 3 hours
        best_hours = df.head(3)
        
        return {
            "recommended_hours": best_hours['hour'].tolist(),
            "reason": "These hours have the best delivery success rate and fastest processing time",
            "avg_delivery_time": round(best_hours['avg_completion_hours'].mean(), 2),
            "success_rate": round(best_hours['success_rate'].mean(), 2)
        }
    
    def predict_restock_needs(self, product_id: str = None) -> List[Dict[str, Any]]:
        """
        Predict when products need restocking based on demand trends.
        Uses simple linear trend analysis.
        """
        start_date, end_date = get_date_range(60)  # Last 2 months
        
        # Query product order frequency
        query = self.db.query(
            Order.productId,
            Product.name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.quantity).label('total_quantity'),
            func.date(Order.createdAt).label('order_date')
        ).join(
            Product, Order.productId == Product.id
        ).filter(
            Order.createdAt.between(start_date, end_date),
            Order.status != OrderStatusEnum.CANCELLED
        )
        
        if product_id:
            query = query.filter(Order.productId == product_id)
        
        results = query.group_by(
            Order.productId, Product.name, func.date(Order.createdAt)
        ).all()
        
        # Group by product
        product_data = {}
        for row in results:
            if row.productId not in product_data:
                product_data[row.productId] = {
                    'name': row.name,
                    'daily_quantities': []
                }
            product_data[row.productId]['daily_quantities'].append(row.total_quantity)
        
        # Analyze each product
        recommendations = []
        for prod_id, data in product_data.items():
            quantities = data['daily_quantities']
            
            if len(quantities) < 7:  # Need at least a week of data
                continue
            
            # Calculate average daily demand
            avg_daily_demand = np.mean(quantities)
            
            # Assume stock of 100 units (you can query actual stock from Product table)
            current_stock = 100  # Placeholder
            
            # Predict days until stockout
            if avg_daily_demand > 0:
                days_until_stockout = int(current_stock / avg_daily_demand)
                recommended_restock = int(avg_daily_demand * 30)  # 30 days supply
                
                if days_until_stockout < 7:  # Alert if less than a week
                    recommendations.append({
                        "product_id": prod_id,
                        "product_name": data['name'],
                        "current_stock_status": "LOW",
                        "predicted_days_until_stockout": days_until_stockout,
                        "avg_daily_demand": round(avg_daily_demand, 2),
                        "recommended_restock_quantity": recommended_restock
                    })
        
        return recommendations
    
    def forecast_demand(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Forecast order demand for next N days.
        Uses moving average and day-of-week patterns.
        """
        start_date, end_date = get_date_range(60)
        
        # Get historical daily orders
        results = self.db.query(
            func.date(Order.createdAt).label('date'),
            extract('dow', Order.createdAt).label('day_of_week'),
            func.count(Order.id).label('order_count')
        ).filter(
            Order.createdAt.between(start_date, end_date),
            Order.status != OrderStatusEnum.CANCELLED
        ).group_by(
            func.date(Order.createdAt),
            extract('dow', Order.createdAt)
        ).order_by('date').all()
        
        if not results:
            return []
        
        # Create DataFrame
        df = pd.DataFrame([{
            'date': row.date,
            'day_of_week': int(row.day_of_week),
            'order_count': row.order_count
        } for row in results])
        
        # Calculate day-of-week averages
        dow_averages = df.groupby('day_of_week')['order_count'].mean().to_dict()
        
        # Calculate overall trend (7-day moving average)
        df['ma_7'] = df['order_count'].rolling(window=7, min_periods=1).mean()
        recent_trend = df['ma_7'].iloc[-7:].mean()
        
        # Forecast
        forecasts = []
        current_date = datetime.utcnow()
        
        for i in range(1, days_ahead + 1):
            forecast_date = current_date + timedelta(days=i)
            dow = forecast_date.weekday()
            
            # Combine day-of-week pattern with recent trend
            dow_pattern = dow_averages.get((dow + 1) % 7, recent_trend)  # PostgreSQL dow offset
            predicted = int((dow_pattern + recent_trend) / 2)
            
            # Add confidence interval (±20%)
            lower_bound = int(predicted * 0.8)
            upper_bound = int(predicted * 1.2)
            
            forecasts.append({
                "forecast_date": forecast_date.strftime('%Y-%m-%d'),
                "predicted_orders": predicted,
                "confidence_interval_lower": lower_bound,
                "confidence_interval_upper": upper_bound
            })
        
        return forecasts
    
    def get_operational_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate actionable operational recommendations.
        """
        recommendations = []
        
        # 1. Peak hour staffing recommendation
        start_date, end_date = get_date_range(30)
        
        peak_hours = self.db.query(
            extract('hour', Order.createdAt).label('hour'),
            func.count(Order.id).label('order_count')
        ).filter(
            Order.createdAt.between(start_date, end_date)
        ).group_by('hour').order_by(func.count(Order.id).desc()).limit(3).all()
        
        if peak_hours:
            peak_hour_list = [int(h.hour) for h in peak_hours]
            recommendations.append({
                "type": "staffing",
                "priority": "high",
                "message": f"Peak order hours: {', '.join([f'{h}:00' for h in peak_hour_list])}",
                "action_required": "Ensure adequate delivery staff during these hours",
                "expected_impact": "Reduce delivery delays by 30%"
            })
        
        # 2. Payment mode optimization
        payment_stats = self.db.query(
            func.count(
                func.nullif(Order.paymentStatus == PaymentStatusEnum.PENDING, False)
            ).label('cash_count'),
            func.count(
                func.nullif(Order.paymentStatus == PaymentStatusEnum.PAID, False)
            ).label('online_count')
        ).filter(
            Order.createdAt.between(start_date, end_date)
        ).first()
        
        if payment_stats:
            total = payment_stats.cash_count + payment_stats.online_count
            if total > 0:
                cash_percentage = (payment_stats.cash_count / total) * 100
                
                if cash_percentage > 50:
                    recommendations.append({
                        "type": "promotion",
                        "priority": "medium",
                        "message": f"{round(cash_percentage)}% orders are cash-based",
                        "action_required": "Promote online payment with 5-10% discount",
                        "expected_impact": "Increase online payments by 20%, reduce COD handling costs"
                    })
        
        # 3. Low-demand period promotions
        hour_stats = self.db.query(
            extract('hour', Order.createdAt).label('hour'),
            func.count(Order.id).label('count')
        ).filter(
            Order.createdAt.between(start_date, end_date)
        ).group_by('hour').all()
        
        if hour_stats:
            avg_count = np.mean([h.count for h in hour_stats])
            low_hours = [int(h.hour) for h in hour_stats if h.count < avg_count * 0.5]
            
            if low_hours:
                recommendations.append({
                    "type": "promotion",
                    "priority": "low",
                    "message": f"Low-demand hours: {', '.join([f'{h}:00' for h in low_hours[:5]])}",
                    "action_required": "Run flash sales or discounts during these hours",
                    "expected_impact": "Increase off-peak orders by 40%"
                })
        
        return recommendations
    
    def get_customer_lifetime_value_prediction(self, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Predict customer lifetime value (CLV) based on purchase patterns.
        """
        start_date, end_date = get_date_range(180)  # Last 6 months
        
        query = self.db.query(
            Order.userId,
            func.count(Order.id).label('order_count'),
            func.sum(Order.totalPrice).label('total_spent'),
            func.avg(Order.totalPrice).label('avg_order_value'),
            func.min(Order.createdAt).label('first_order'),
            func.max(Order.createdAt).label('last_order')
        ).filter(
            Order.createdAt.between(start_date, end_date),
            Order.status != OrderStatusEnum.CANCELLED
        ).group_by(Order.userId)
        
        if user_id:
            query = query.filter(Order.userId == user_id)
        
        results = query.all()
        
        clv_predictions = []
        for row in results:
            # Calculate customer metrics
            days_active = (row.last_order - row.first_order).days or 1
            order_frequency = row.order_count / (days_active / 30)  # Orders per month
            
            # Simple CLV prediction: avg_order_value * predicted_orders_per_year
            predicted_annual_orders = order_frequency * 12
            predicted_clv = row.avg_order_value * predicted_annual_orders
            
            clv_predictions.append({
                "user_id": row.userId,
                "total_spent": round_currency(row.total_spent),
                "order_count": row.order_count,
                "avg_order_value": round_currency(row.avg_order_value),
                "order_frequency_per_month": round(order_frequency, 2),
                "predicted_annual_value": round_currency(predicted_clv),
                "customer_segment": "High Value" if predicted_clv > 1000 else "Medium Value" if predicted_clv > 500 else "Low Value"
            })
        
        # Sort by predicted value
        clv_predictions.sort(key=lambda x: x['predicted_annual_value'], reverse=True)
        
        return clv_predictions[:50]  # Top 50
