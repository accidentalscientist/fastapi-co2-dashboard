from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import asyncio
import os
import logging

from db import get_database
from services.data_service import DataService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
data_service = DataService()

async def update_sustainability_data():
    """Background job to update sustainability data"""
    try:
        db = await get_database()
        await data_service.seed_historical_data(db)
    except Exception as e:
        logger.error(f"Error in scheduled data update: {e}")

def start_scheduler():
    """Start the background scheduler"""
    try:
        # Get interval from environment
        interval_minutes = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", 1))
        
        # Add job
        scheduler.add_job(
            update_sustainability_data,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id="sustainability_data_update",
            name="Update Sustainability Data",
            replace_existing=True
        )
        
        # Start scheduler
        scheduler.start()
        logger.info(f"Scheduler started with {interval_minutes} minute interval")
        
        # Run initial data update
        asyncio.create_task(update_sustainability_data())
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")

def stop_scheduler():
    """Stop the background scheduler"""
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")

def get_scheduler_status():
    """Get scheduler status"""
    return {
        "running": scheduler.running if scheduler else False,
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in scheduler.get_jobs()
        ] if scheduler and scheduler.running else []
    }