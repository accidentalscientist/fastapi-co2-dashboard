from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from db import connect_to_mongo, close_mongo_connection
from routers import dashboard
from services.scheduler import start_scheduler, stop_scheduler
from services.data_service import DataService

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()
    await close_mongo_connection()

app = FastAPI(
    title="Sustainability Dashboard API",
    description="API for sustainability metrics and dashboard data",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"])

@app.get("/")
async def root():
    return {"message": "Sustainability Dashboard API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host=host, port=port)