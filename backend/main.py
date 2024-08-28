from fastapi import FastAPI
from utils.init_db import create_tables
from router.api import api_router

app = FastAPI(
    debug=True,
    title="Internship Tracker",
)

@app.on_event("startup")
def on_startup():
    create_tables()

app.include_router(api_router)

