# ⚡ QUICK START GUIDE

Get your analytics backend running in **5 minutes**!

---

## 📋 Prerequisites

- ✅ Python 3.9 or higher
- ✅ PostgreSQL database (from your Next.js app)
- ✅ Redis (optional, for caching)

---

## 🚀 3 Simple Steps

### **Step 1: Install**

```bash
# Navigate to project
cd fastapi-analytics-backend

# Run setup script (Linux/Mac)
bash setup.sh

# OR manually:
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### **Step 2: Configure**

Edit `.env` file:

```env
# REQUIRED: Your PostgreSQL database URL
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Example:
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/marketplace_db

# OPTIONAL: Redis for caching (leave default if not using)
REDIS_HOST=localhost
REDIS_PORT=6379

# OPTIONAL: CORS origins (add your Next.js URL)
ALLOWED_ORIGINS=http://localhost:3000
```

**💡 Tip:** Use the **same database** as your Next.js application!

---

### **Step 3: Run**

```bash
# Start the server
python run.py

# OR
uvicorn app.main:app --reload
```

✅ **That's it!** Your API is now running at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs ← **Start here!**

---

## 🧪 Test Your API

### **Option 1: Interactive Docs** (Recommended)

1. Visit: http://localhost:8000/docs
2. Click any endpoint
3. Click "Try it out"
4. Click "Execute"
5. See the results!

### **Option 2: Command Line**

```bash
# Test payment overview
curl http://localhost:8000/api/v1/finance/overview

# Test peak hours
curl http://localhost:8000/api/v1/orders/peak-hours

# Test recommendations
curl http://localhost:8000/api/v1/recommendations/best-order-time
```

### **Option 3: Your Next.js App**

```typescript
// Add to your Next.js app
const response = await fetch('http://localhost:8000/api/v1/finance/overview');
const data = await response.json();
console.log(data);
```

---

## 📊 What Can You Do Now?

### **Explore Analytics:**
- 💰 Financial: Cash vs Online payments
- 📦 Orders: Peak hours, trends, growth
- 👥 Customers: Segmentation, lifetime value
- 🛍️ Products: Best sellers, stock alerts
- 🔧 Services: Bookings, provider performance
- 🗺️ Geography: Heatmaps, delivery zones

### **Get Recommendations:**
- 🤖 Best order times
- 🤖 Restock predictions
- 🤖 Demand forecasting
- 🤖 Operational insights

---

## 🎯 Key Endpoints to Try

| What You Want | Endpoint |
|---------------|----------|
| Payment breakdown | `/api/v1/finance/overview` |
| Peak hours | `/api/v1/orders/peak-hours` |
| Best sellers | `/api/v1/products/best-sellers` |
| Customer insights | `/api/v1/customers/segmentation` |
| Recommendations | `/api/v1/recommendations/operations` |

**Full list:** See `ENDPOINTS.md`

---

## 🔧 Troubleshooting

### **Issue: "Connection refused"**
→ Make sure the server is running (`python run.py`)

### **Issue: "Database connection error"**
→ Check your `DATABASE_URL` in `.env` file

### **Issue: "Empty results"**
→ Your database might not have data yet. Create some orders first!

### **Issue: "Module not found"**
→ Make sure you activated the virtual environment:
```bash
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

---

## 📚 Next Steps

1. ✅ **Explore the docs**: http://localhost:8000/docs
2. ✅ **Read**: `API_TESTING_GUIDE.md` for examples
3. ✅ **Check**: `ENDPOINTS.md` for all 50+ endpoints
4. ✅ **Learn**: `README.md` for detailed documentation
5. ✅ **Integrate**: Connect to your Next.js frontend

---

## 💡 Pro Tips

1. **Use the interactive docs** - It's the easiest way to test
2. **Enable Redis** - For faster responses (optional)
3. **Check the logs** - Server prints helpful debug info
4. **Start simple** - Test `/finance/overview` first
5. **Read responses** - They're self-explanatory JSON

---

## 🎉 You're Ready!

Your analytics backend is now running and ready to provide insights!

**Questions?** Check the documentation files:
- `README.md` - Complete guide
- `ENDPOINTS.md` - All endpoints
- `API_TESTING_GUIDE.md` - Testing examples
- `PROJECT_SUMMARY.md` - Overview

**Happy analyzing!** 📊🚀
