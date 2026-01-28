# 🚀 FastAPI Analytics Backend

Complete analytics and ML-powered recommendation engine for your Next.js marketplace platform.

## 📊 Features

### **Financial Analytics**
- ✅ Cash vs Online payment breakdown
- ✅ Revenue trends (daily, weekly, monthly)
- ✅ Payment mode patterns by hour
- ✅ Failed payment tracking
- ✅ Refund analysis

### **Order Analytics**
- ✅ Peak hours analysis (0-23 hours)
- ✅ Day of week patterns
- ✅ Order velocity & growth rates
- ✅ Status conversion funnel
- ✅ Timeline preference analysis

### **Customer Analytics**
- ✅ Customer segmentation (high-value, frequent buyers)
- ✅ Geographic distribution
- ✅ Lifetime value prediction
- ✅ New vs returning customers
- ✅ Demographics analysis

### **Product Analytics**
- ✅ Best-selling products
- ✅ Category performance
- ✅ Price performance analysis
- ✅ Trending products
- ✅ Stock alerts

### **Service Analytics**
- ✅ Popular services
- ✅ Provider performance
- ✅ Location-based demand
- ✅ Booking trends
- ✅ Category analysis

### **ML-Powered Recommendations**
- 🤖 Best time to order suggestions
- 🤖 Restock predictions
- 🤖 Demand forecasting (7-day)
- 🤖 Operational recommendations
- 🤖 Pricing optimization
- 🤖 Customer retention strategies

### **Geographic Analytics**
- 🗺️ Order heatmaps
- 🗺️ Delivery zone optimization
- 🗺️ State-level performance
- 🗺️ Distance analysis

---

## 🛠️ Installation

### **Prerequisites**
- Python 3.9+
- PostgreSQL database (from your Next.js app)
- Redis (optional, for caching)

### **Step 1: Clone & Install**

```bash
cd fastapi-analytics-backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 2: Configure Environment**

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
# Database - Use the same database as your Next.js app
DATABASE_URL=postgresql://username:password@localhost:5432/your_database_name

# Example:
# DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/marketplace_db

# Redis (optional - for caching)
REDIS_HOST=localhost
REDIS_PORT=6379

# CORS - Add your Next.js frontend URL
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### **Step 3: Run the Server**

```bash
# Development mode (with auto-reload)
python run.py

# OR
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 API Endpoints

### **Financial Analytics** (`/api/v1/finance`)

| Endpoint | Description |
|----------|-------------|
| `GET /overview` | Complete payment breakdown (cash vs online) |
| `GET /trends?days=30` | Daily payment trends over time |
| `GET /hourly-patterns` | Which hours prefer cash vs online |
| `GET /revenue-summary` | Complete revenue summary with insights |

### **Order Analytics** (`/api/v1/orders`)

| Endpoint | Description |
|----------|-------------|
| `GET /peak-hours?days=30` | Hourly order breakdown (0-23) |
| `GET /day-of-week?days=30` | Monday-Sunday patterns |
| `GET /velocity` | Order growth rates (WoW, MoM) |
| `GET /funnel` | Status conversion funnel |
| `GET /timeline-analysis` | IMMEDIATE vs scheduled orders |
| `GET /status-distribution` | Current order status breakdown |

### **Customer Analytics** (`/api/v1/customers`)

| Endpoint | Description |
|----------|-------------|
| `GET /segmentation` | High-value, frequent buyers, cash/online users |
| `GET /geographic` | Top locations by orders & revenue |
| `GET /lifetime-value?limit=50` | Predicted customer CLV |
| `GET /demographics` | Gender, user types, verification stats |
| `GET /new-vs-returning?days=30` | Customer acquisition & retention |

### **Product Analytics** (`/api/v1/products`)

| Endpoint | Description |
|----------|-------------|
| `GET /best-sellers?limit=20` | Top products by orders & revenue |
| `GET /category-performance` | Category-wise sales analysis |
| `GET /stock-alerts` | Products needing restock (ML-based) |
| `GET /price-performance` | Which price ranges sell best |
| `GET /trending?days=7` | Products gaining popularity |

### **Service Analytics** (`/api/v1/services`)

| Endpoint | Description |
|----------|-------------|
| `GET /popular?limit=20` | Most booked services |
| `GET /provider-performance` | Top service providers |
| `GET /location-demand` | Geographic service demand |
| `GET /booking-trends?days=30` | Daily booking patterns |
| `GET /service-categories` | Category performance |

### **Recommendations** (`/api/v1/recommendations`)

| Endpoint | Description |
|----------|-------------|
| `GET /best-order-time` | Optimal ordering hours for customers |
| `GET /restock` | Predicted restock needs |
| `GET /demand-forecast?days_ahead=7` | 7-day order forecast |
| `GET /operations` | Staffing, promotions, inventory recommendations |
| `GET /pricing-insights` | Price optimization suggestions |
| `GET /customer-retention` | At-risk customers & win-back strategies |

### **Geographic Analytics** (`/api/v1/geography`)

| Endpoint | Description |
|----------|-------------|
| `GET /heatmap` | City & pincode order density |
| `GET /delivery-zones` | Zone optimization analysis |
| `GET /state-performance` | State-level metrics |
| `GET /distance-analysis` | Service radius analysis |

---

## 📊 Example API Calls

### **Get Payment Overview**

```bash
curl http://localhost:8000/api/v1/finance/overview
```

**Response:**
```json
{
  "total_revenue": 150000.50,
  "cash_revenue": 60000.25,
  "online_revenue": 90000.25,
  "cash_percentage": 40.0,
  "online_percentage": 60.0,
  "failed_payments_loss": 5000.0,
  "refunded_amount": 2000.0,
  "pending_cod": 60000.25
}
```

### **Get Peak Hours**

```bash
curl http://localhost:8000/api/v1/orders/peak-hours?days=30
```

**Response:**
```json
[
  {
    "hour": 14,
    "order_count": 245,
    "total_revenue": 35000.50,
    "avg_order_value": 142.86
  },
  {
    "hour": 18,
    "order_count": 320,
    "total_revenue": 48000.00,
    "avg_order_value": 150.00
  }
]
```

### **Get Best Order Time Recommendation**

```bash
curl http://localhost:8000/api/v1/recommendations/best-order-time
```

**Response:**
```json
{
  "recommended_hours": [14, 15, 16],
  "reason": "These hours have the best delivery success rate and fastest processing time",
  "avg_delivery_time": 3.5,
  "success_rate": 95.5
}
```

---

## 🔧 Configuration Options

### **Cache Settings**

Enable/disable caching in `.env`:

```env
CACHE_ENABLED=True
CACHE_TTL=300  # 5 minutes
```

### **Pagination**

```env
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### **CORS**

Add multiple origins:

```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,https://yourdomain.com
```

---

## 🎯 Integration with Next.js

### **Frontend Example (Next.js)**

```typescript
// lib/analytics.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_ANALYTICS_API || 'http://localhost:8000';

export async function getPaymentOverview() {
  const response = await fetch(`${API_BASE_URL}/api/v1/finance/overview`);
  return response.json();
}

export async function getPeakHours(days: number = 30) {
  const response = await fetch(`${API_BASE_URL}/api/v1/orders/peak-hours?days=${days}`);
  return response.json();
}

export async function getBestSellers(limit: number = 20) {
  const response = await fetch(`${API_BASE_URL}/api/v1/products/best-sellers?limit=${limit}`);
  return response.json();
}
```

### **React Component Example**

```tsx
'use client';

import { useEffect, useState } from 'react';
import { getPaymentOverview } from '@/lib/analytics';

export default function FinancialDashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    getPaymentOverview().then(setData);
  }, []);

  if (!data) return <div>Loading...</div>;

  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="p-4 bg-white rounded shadow">
        <h3>Total Revenue</h3>
        <p className="text-2xl">₹{data.total_revenue}</p>
      </div>
      <div className="p-4 bg-white rounded shadow">
        <h3>Online Payments</h3>
        <p className="text-2xl">{data.online_percentage}%</p>
      </div>
      <div className="p-4 bg-white rounded shadow">
        <h3>Cash Payments</h3>
        <p className="text-2xl">{data.cash_percentage}%</p>
      </div>
    </div>
  );
}
```

---

## 🚀 Deployment

### **Using Docker**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Using Gunicorn (Production)**

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📈 Performance Tips

1. **Enable Redis caching** for faster responses
2. **Use connection pooling** for database (already configured)
3. **Add indexes** to your Postgres tables:
   ```sql
   CREATE INDEX idx_orders_created_at ON "Order" (createdAt);
   CREATE INDEX idx_orders_user_id ON "Order" (userId);
   CREATE INDEX idx_orders_product_id ON "Order" (productId);
   ```

---

## 🤝 Support

For issues or questions:
1. Check the API documentation: http://localhost:8000/docs
2. Review this README
3. Contact your development team

---

## 📄 License

Proprietary - Internal use only

---

**Built with ❤️ using FastAPI, SQLAlchemy, and Pandas**
# analysis_backend
# analysis_backend
