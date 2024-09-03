from fastapi import APIRouter
from router.v1 import internship_router
from router.v1 import email_router

api_router = APIRouter(
    prefix="/api/v1"
)

api_router.include_router(internship_router.router)
api_router.include_router(email_router.router)