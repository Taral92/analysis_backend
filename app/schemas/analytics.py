"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


# ===== FINANCIAL ANALYTICS =====
class PaymentBreakdown(BaseModel):
    total_revenue: float
    cash_revenue: float
    online_revenue: float
    cash_percentage: float
    online_percentage: float
    failed_payments_loss: float
    refunded_amount: float
    pending_cod: float


class PaymentTrendData(BaseModel):
    date: str
    cash_amount: float
    online_amount: float
    total_amount: float


class PaymentTrendsResponse(BaseModel):
    trends: List[PaymentTrendData]
    summary: PaymentBreakdown


class HourlyPaymentData(BaseModel):
    hour: int
    cash_orders: int
    online_orders: int
    cash_amount: float
    online_amount: float


# ===== ORDER ANALYTICS =====
class PeakHourData(BaseModel):
    hour: int
    order_count: int
    total_revenue: float
    avg_order_value: float


class DayOfWeekData(BaseModel):
    day: str
    day_number: int
    order_count: int
    total_revenue: float


class OrderVelocity(BaseModel):
    period: str  # "hourly", "daily", "weekly", "monthly"
    current_value: float
    previous_value: float
    growth_rate: float
    moving_average_7d: Optional[float] = None
    moving_average_30d: Optional[float] = None


class OrderFunnel(BaseModel):
    pending: int
    confirmed: int
    shipped: int
    out_for_delivery: int
    delivered: int
    cancelled: int
    returned: int
    conversion_rate: float
    cancellation_rate: float


# ===== CUSTOMER ANALYTICS =====
class CustomerSegment(BaseModel):
    segment_name: str
    customer_count: int
    total_revenue: float
    avg_order_value: float
    order_count: int


class CustomerLifetimeValue(BaseModel):
    user_id: str
    user_name: Optional[str]
    total_spent: float
    order_count: int
    avg_order_value: float
    first_order_date: datetime
    last_order_date: datetime


class GeographicData(BaseModel):
    location: str  # city, state, or pincode
    order_count: int
    revenue: float
    customer_count: int


# ===== PRODUCT ANALYTICS =====
class ProductPerformance(BaseModel):
    product_id: str
    product_name: str
    order_count: int
    total_quantity: int
    total_revenue: float
    avg_price: float


class CategoryPerformance(BaseModel):
    category_id: str
    category_name: str
    product_count: int
    order_count: int
    total_revenue: float


# ===== SERVICE ANALYTICS =====
class ServicePerformance(BaseModel):
    service_id: str
    service_name: str
    booking_count: int
    avg_rating: float
    provider_name: Optional[str]


# ===== RECOMMENDATIONS =====
class BestTimeRecommendation(BaseModel):
    recommended_hours: List[int]
    reason: str
    avg_delivery_time: float
    success_rate: float


class RestockRecommendation(BaseModel):
    product_id: str
    product_name: str
    current_stock_status: str
    predicted_days_until_stockout: int
    recommended_restock_quantity: int


class DemandForecast(BaseModel):
    forecast_date: str
    predicted_orders: int
    confidence_interval_lower: int
    confidence_interval_upper: int


class OperationalRecommendation(BaseModel):
    type: str  # "staffing", "promotion", "inventory"
    priority: str  # "high", "medium", "low"
    message: str
    action_required: str
    expected_impact: str


# ===== GENERIC RESPONSES =====
class TimeSeriesData(BaseModel):
    timestamp: str
    value: float
    label: Optional[str] = None


class GenericResponse(BaseModel):
    success: bool
    message: str
    data: Any


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[Any]
