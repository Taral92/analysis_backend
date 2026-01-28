"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import (
    finance,
    orders,
    customers,
    products,
    services,
    geography,
    recommendations
)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    🚀 **Analytics API for Marketplace Platform**
    
    Comprehensive analytics and ML-powered recommendations for:
    - Financial insights (Cash vs Online payments)
    - Order analytics (Peak hours, trends, funnels)
    - Customer segmentation & lifetime value
    - Product performance & demand forecasting
    - Service bookings & provider analytics
    - Geographic analysis & delivery optimization
    - Operational recommendations
    
    **Features:**
    - Real-time analytics
    - ML-based forecasting
    - Cached responses for performance
    - Comprehensive business insights
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "Analytics API is running",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "analytics-api",
        "version": settings.VERSION
    }


# Include routers
app.include_router(finance.router, prefix=settings.API_V1_PREFIX)
app.include_router(orders.router, prefix=settings.API_V1_PREFIX)
app.include_router(customers.router, prefix=settings.API_V1_PREFIX)
app.include_router(products.router, prefix=settings.API_V1_PREFIX)
app.include_router(services.router, prefix=settings.API_V1_PREFIX)
app.include_router(geography.router, prefix=settings.API_V1_PREFIX)
app.include_router(recommendations.router, prefix=settings.API_V1_PREFIX)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all uncaught exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("=" * 50)
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📊 Analytics API starting...")
    print(f"🔧 Debug mode: {settings.DEBUG}")
    print(f"💾 Database: Connected")
    print(f"🗄️  Cache: {'Enabled' if settings.CACHE_ENABLED else 'Disabled'}")
    print("=" * 50)
    print(f"📖 API Documentation: http://localhost:8000/docs")
    print(f"📚 ReDoc: http://localhost:8000/redoc")
    print("=" * 50)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("🛑 Shutting down Analytics API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
