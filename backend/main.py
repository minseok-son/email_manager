from fastapi import FastAPI
from utils.init_db import create_tables
from router.api import api_router
from celery_files.tasks import hourly_task
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()  # Writes logs to the console
    ]
)
app = FastAPI(
    debug=True,
    title="Internship Tracker",
)

@app.on_event("startup")
def on_startup():
    create_tables()

@app.get("/trigger-hourly-task")
async def trigger_hourly_task():
    task = hourly_task.delay()
    return {"task_id": task.id}

app.include_router(api_router)

