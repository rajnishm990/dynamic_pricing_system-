from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from app.api.routes import pricing, weather,events 
from app.core.config import settings 
from app.db.database import init_db


app = FastAPI(
    title = settings.APP_NAME,
    description = "Dynamic pricing engine for menu items based on itnernal as well external factors ",
    version = settings.APP_VERSION ,
    docs_url ="/docs",
    redoc_url = "/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pricing.router)
app.include_router(weather.router)
app.include_router(events.router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print(f"{settings.APP_NAME} started succesfully!") 


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": f"{settings.APP_NAME} is running",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.APP_VERSION
    }