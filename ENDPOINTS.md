# 📡 Complete API Endpoint Reference

Base URL: `http://localhost:8000/api/v1`

---

## 💰 Financial Analytics

### GET `/finance/overview`
**Description:** Complete payment breakdown - Cash vs Online  
**Query Parameters:**
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)

**Response:**
- Total revenue
- Cash revenue & percentage
- Online revenue & percentage
- Failed payments (lost revenue)
- Refunded amounts

---

### GET `/finance/trends`
**Description:** Daily payment trends over time  
**Query Parameters:**
- `days` (default: 30): Number of days to analyze

**Response:**
- Daily breakdown of cash vs online
- Summary statistics

---

### GET `/finance/hourly-patterns`
**Description:** Analyze which hours prefer cash vs online payments  

**Response:**
- Hourly breakdown (0-23)
- Cash vs online orders per hour
- Revenue by payment method per hour

---

### GET `/finance/revenue-summary`
**Description:** Complete revenue summary with insights  
**Query Parameters:**
- `days` (default: 30): Number of days

**Response:**
- Payment breakdown
- Growth metrics
- Business insights

---

## 📦 Order Analytics

### GET `/orders/peak-hours`
**Description:** Hourly order breakdown (0-23)  
**Query Parameters:**
- `days` (default: 30): Number of days to analyze

**Response:**
- Order count per hour
- Revenue per hour
- Average order value per hour

---

### GET `/orders/day-of-week`
**Description:** Monday-Sunday order patterns  
**Query Parameters:**
- `days` (default: 30): Number of days to analyze

**Response:**
- Order count per day
- Revenue per day
- Day names (Monday-Sunday)

---

### GET `/orders/velocity`
**Description:** Order growth rates (WoW, MoM)  

**Response:**
- Weekly metrics (current vs previous)
- Monthly metrics (current vs previous)
- Growth rates

---

### GET `/orders/funnel`
**Description:** Order status conversion funnel  

**Response:**
- Count per status (PENDING → DELIVERED)
- Conversion rate
- Cancellation rate

---

### GET `/orders/timeline-analysis`
**Description:** IMMEDIATE vs scheduled orders analysis  

**Response:**
- Order count per timeline type
- Percentage breakdown
- Average completion hours

---

### GET `/orders/status-distribution`
**Description:** Current order status breakdown (last 7 days)  

**Response:**
- Orders per status
- Real-time snapshot

---

## 👥 Customer Analytics

### GET `/customers/segmentation`
**Description:** Customer segments by behavior and value  

**Response:**
- High-value customers (top 20)
- Frequent buyers (top 20)
- Cash-only vs online-only user counts
- Total customer count

---

### GET `/customers/geographic`
**Description:** Customer & order distribution by location  

**Response:**
- Top 50 locations by:
  - Order count
  - Revenue
  - Customer count
- Breakdown by city/state/pincode

---

### GET `/customers/lifetime-value`
**Description:** Predicted customer lifetime value  
**Query Parameters:**
- `limit` (default: 50): Number of customers to return

**Response:**
- User ID & name
- Total spent
- Order count
- Predicted annual value
- Customer segment

---

### GET `/customers/demographics`
**Description:** Customer demographics analysis  

**Response:**
- Gender distribution
- User types (workers vs customers)
- Verification status

---

### GET `/customers/new-vs-returning`
**Description:** Customer acquisition & retention  
**Query Parameters:**
- `days` (default: 30): Number of days to analyze

**Response:**
- New customer count
- Returning customer count
- Retention rate

---

## 🛍️ Product Analytics

### GET `/products/best-sellers`
**Description:** Top-selling products  
**Query Parameters:**
- `limit` (default: 20): Number of products to return

**Response:**
- Product ID & name
- Order count
- Total quantity sold
- Total revenue
- Average price

---

### GET `/products/category-performance`
**Description:** Category-wise sales analysis  

**Response:**
- Category ID & name
- Product count per category
- Order count per category
- Total revenue per category

---

### GET `/products/stock-alerts`
**Description:** Products needing restock (ML-based)  

**Response:**
- Product ID & name
- Current stock status
- Predicted days until stockout
- Average daily demand
- Recommended restock quantity

---

### GET `/products/price-performance`
**Description:** Which price ranges perform best  

**Response:**
- Price range
- Order count
- Total revenue
- Average order value

---

### GET `/products/trending`
**Description:** Products gaining popularity  
**Query Parameters:**
- `days` (default: 7): Compare with this many days ago

**Response:**
- Product ID & name
- Current vs previous orders
- Growth rate
- Top 20 trending products

---

## 🔧 Service Analytics

### GET `/services/popular`
**Description:** Most booked services  
**Query Parameters:**
- `limit` (default: 20): Number of services to return

**Response:**
- Service ID & name
- Booking count
- Average rating
- Provider name

---

### GET `/services/provider-performance`
**Description:** Service provider performance rankings  

**Response:**
- Provider ID & name
- Total bookings
- Completed bookings
- Completion rate
- Average rating
- Services offered

---

### GET `/services/location-demand`
**Description:** Geographic service demand  

**Response:**
- City/state/pincode
- Booking count per location
- Top 50 locations

---

### GET `/services/booking-trends`
**Description:** Daily booking patterns  
**Query Parameters:**
- `days` (default: 30): Number of days to analyze

**Response:**
- Date
- Booking count per day

---

### GET `/services/service-categories`
**Description:** Service category performance  

**Response:**
- Category ID & name
- Booking count
- Average rating
- Service count

---

## 🤖 ML-Powered Recommendations

### GET `/recommendations/best-order-time`
**Description:** Optimal ordering hours for customers  

**Response:**
- Recommended hours (top 3)
- Reason
- Average delivery time
- Success rate

---

### GET `/recommendations/restock`
**Description:** Predicted restock needs  
**Query Parameters:**
- `product_id` (optional): Specific product ID

**Response:**
- Products needing urgent restock
- Days until stockout
- Recommended quantities

---

### GET `/recommendations/demand-forecast`
**Description:** 7-day order demand forecast  
**Query Parameters:**
- `days_ahead` (default: 7): Number of days to forecast

**Response:**
- Forecast date
- Predicted orders
- Confidence intervals (upper/lower bounds)

---

### GET `/recommendations/operations`
**Description:** Actionable operational recommendations  

**Response:**
- Type (staffing, promotion, inventory)
- Priority (high, medium, low)
- Message
- Action required
- Expected impact

---

### GET `/recommendations/pricing-insights`
**Description:** Price optimization suggestions  

**Response:**
- Product ID & name
- Current price
- Order count
- Recommendation
- Reasoning

---

### GET `/recommendations/customer-retention`
**Description:** At-risk customers & win-back strategies  

**Response:**
- User ID, name, email
- Days since last order
- Lifetime value
- Recommendation
- Priority

---

## 🗺️ Geographic Analytics

### GET `/geography/heatmap`
**Description:** Order density heatmap  

**Response:**
- City heatmap (order count, revenue)
- Pincode heatmap (order count)
- Top 100 locations

---

### GET `/geography/delivery-zones`
**Description:** Delivery zone optimization  

**Response:**
- City/pincode
- Total orders
- Delivered orders
- Delivery success rate
- Average delivery hours
- Zone type (high/medium/low demand)

---

### GET `/geography/state-performance`
**Description:** State-level performance metrics  

**Response:**
- State
- Order count
- Total revenue
- Average order value
- Customer count

---

### GET `/geography/distance-analysis`
**Description:** Service radius analysis  

**Response:**
- Services with location data
- Radius distribution
- Distance patterns (if geocoding available)

---

## 🏥 Health & System

### GET `/`
**Description:** Root endpoint - API health check  

**Response:**
- API status
- Version
- Documentation links

---

### GET `/health`
**Description:** Health check endpoint  

**Response:**
- Service status
- Version

---

## 📊 Response Formats

All endpoints return JSON responses.

**Success Response:**
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error (if DEBUG=True)"
}
```

---

## 🔐 CORS Configuration

The API supports CORS for the following origins (configurable in `.env`):
- http://localhost:3000
- http://localhost:3001
- Add your production domain

---

## ⚡ Caching

Most analytics endpoints are cached for 5 minutes (300 seconds) by default.  
Recommendations are cached for 10 minutes (600 seconds).

Configure in `.env`:
```
CACHE_ENABLED=True
CACHE_TTL=300
```

---

## 📈 Rate Limiting

Currently no rate limiting is implemented.  
For production, consider adding rate limiting using:
- fastapi-limiter
- slowapi
- nginx rate limiting

---

**Total Endpoints: 50+**
