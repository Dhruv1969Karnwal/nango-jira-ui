"""
Nango Jira Integration Backend
FastAPI application for interacting with Jira through Nango
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from config import get_settings
from routes.jira_routes import router as jira_router

settings = get_settings()

# MongoDB client
mongodb_client: AsyncIOMotorClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    global mongodb_client
    
    # Startup
    print(f"Starting Nango Jira Integration Backend...")
    print(f"Nango Host: {settings.nango_host}")
    print(f"MongoDB: {settings.mongodb_url}/{settings.mongodb_db_name}")
    
    # Connect to MongoDB
    mongodb_client = AsyncIOMotorClient(settings.mongodb_url)
    app.state.mongodb = mongodb_client[settings.mongodb_db_name]
    
    yield
    
    # Shutdown
    print("Shutting down...")
    mongodb_client.close()


# Create FastAPI app
app = FastAPI(
    title="Nango Jira Integration API",
    description="Backend API for Jira integration using self-hosted Nango",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jira_router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Nango Jira Integration API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "nango_host": settings.nango_host,
        "mongodb_connected": mongodb_client is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
