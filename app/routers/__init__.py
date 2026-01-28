"""
API route handlers.
"""
from app.routers import finance, orders, customers, products, services, geography, recommendations

__all__ = [
    "finance",
    "orders",
    "customers",
    "products",
    "services",
    "geography",
    "recommendations",
]
