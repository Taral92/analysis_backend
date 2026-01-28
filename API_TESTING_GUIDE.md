# 🧪 API Testing Guide

Quick reference for testing all analytics endpoints.

## 🚀 Quick Start

```bash
# Start the server
python run.py

# The API will be running at http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

---

## 📊 Financial Analytics Tests

### 1. Payment Overview
```bash
curl http://localhost:8000/api/v1/finance/overview
```

### 2. Payment Trends (Last 30 Days)
```bash
curl http://localhost:8000/api/v1/finance/trends?days=30
```

### 3. Hourly Payment Patterns
```bash
curl http://localhost:8000/api/v1/finance/hourly-patterns
```

### 4. Revenue Summary
```bash
curl http://localhost:8000/api/v1/finance/revenue-summary
```

---

## 📦 Order Analytics Tests

### 1. Peak Hours
```bash
curl http://localhost:8000/api/v1/orders/peak-hours?days=30
```

### 2. Day of Week Analysis
```bash
curl http://localhost:8000/api/v1/orders/day-of-week?days=30
```

### 3. Order Velocity (Growth Rates)
```bash
curl http://localhost:8000/api/v1/orders/velocity
```

### 4. Order Funnel
```bash
curl http://localhost:8000/api/v1/orders/funnel
```

### 5. Timeline Analysis
```bash
curl http://localhost:8000/api/v1/orders/timeline-analysis
```

---

## 👥 Customer Analytics Tests

### 1. Customer Segmentation
```bash
curl http://localhost:8000/api/v1/customers/segmentation
```

### 2. Geographic Analysis
```bash
curl http://localhost:8000/api/v1/customers/geographic
```

### 3. Lifetime Value
```bash
curl http://localhost:8000/api/v1/customers/lifetime-value?limit=50
```

### 4. Demographics
```bash
curl http://localhost:8000/api/v1/customers/demographics
```

### 5. New vs Returning
```bash
curl http://localhost:8000/api/v1/customers/new-vs-returning?days=30
```

---

## 🛍️ Product Analytics Tests

### 1. Best Sellers
```bash
curl http://localhost:8000/api/v1/products/best-sellers?limit=20
```

### 2. Category Performance
```bash
curl http://localhost:8000/api/v1/products/category-performance
```

### 3. Stock Alerts
```bash
curl http://localhost:8000/api/v1/products/stock-alerts
```

### 4. Price Performance
```bash
curl http://localhost:8000/api/v1/products/price-performance
```

### 5. Trending Products
```bash
curl http://localhost:8000/api/v1/products/trending?days=7
```

---

## 🔧 Service Analytics Tests

### 1. Popular Services
```bash
curl http://localhost:8000/api/v1/services/popular?limit=20
```

### 2. Provider Performance
```bash
curl http://localhost:8000/api/v1/services/provider-performance
```

### 3. Location Demand
```bash
curl http://localhost:8000/api/v1/services/location-demand
```

### 4. Booking Trends
```bash
curl http://localhost:8000/api/v1/services/booking-trends?days=30
```

---

## 🤖 Recommendations Tests

### 1. Best Order Time
```bash
curl http://localhost:8000/api/v1/recommendations/best-order-time
```

### 2. Restock Predictions
```bash
curl http://localhost:8000/api/v1/recommendations/restock
```

### 3. Demand Forecast
```bash
curl http://localhost:8000/api/v1/recommendations/demand-forecast?days_ahead=7
```

### 4. Operational Recommendations
```bash
curl http://localhost:8000/api/v1/recommendations/operations
```

### 5. Pricing Insights
```bash
curl http://localhost:8000/api/v1/recommendations/pricing-insights
```

### 6. Customer Retention
```bash
curl http://localhost:8000/api/v1/recommendations/customer-retention
```

---

## 🗺️ Geographic Analytics Tests

### 1. Order Heatmap
```bash
curl http://localhost:8000/api/v1/geography/heatmap
```

### 2. Delivery Zones
```bash
curl http://localhost:8000/api/v1/geography/delivery-zones
```

### 3. State Performance
```bash
curl http://localhost:8000/api/v1/geography/state-performance
```

---

## 🧪 Testing with Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Test payment overview
response = requests.get(f"{BASE_URL}/finance/overview")
print(response.json())

# Test peak hours
response = requests.get(f"{BASE_URL}/orders/peak-hours", params={"days": 30})
print(response.json())

# Test best sellers
response = requests.get(f"{BASE_URL}/products/best-sellers", params={"limit": 10})
print(response.json())
```

---

## 🧪 Testing with JavaScript/TypeScript

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// Test payment overview
fetch(`${BASE_URL}/finance/overview`)
  .then(res => res.json())
  .then(data => console.log(data));

// Test peak hours
fetch(`${BASE_URL}/orders/peak-hours?days=30`)
  .then(res => res.json())
  .then(data => console.log(data));

// Test recommendations
fetch(`${BASE_URL}/recommendations/best-order-time`)
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 🎯 Expected Response Formats

### Payment Overview
```json
{
  "total_revenue": 150000.50,
  "cash_revenue": 60000.25,
  "online_revenue": 90000.25,
  "cash_percentage": 40.0,
  "online_percentage": 60.0,
  "failed_payments_loss": 5000.0,
  "refunded_amount": 2000.0
}
```

### Peak Hours
```json
[
  {
    "hour": 14,
    "order_count": 245,
    "total_revenue": 35000.50,
    "avg_order_value": 142.86
  }
]
```

### Best Sellers
```json
[
  {
    "product_id": "abc123",
    "product_name": "Product Name",
    "order_count": 150,
    "total_quantity": 300,
    "total_revenue": 45000.00,
    "avg_price": 150.00
  }
]
```

---

## ⚠️ Common Issues

### Issue: Connection Error
**Solution:** Make sure the server is running on port 8000

### Issue: Database Error
**Solution:** Check your `.env` file has correct DATABASE_URL

### Issue: Empty Results
**Solution:** Your database might not have data yet. Add some orders first.

---

## 📖 Interactive Documentation

Visit http://localhost:8000/docs for interactive API testing with Swagger UI!
