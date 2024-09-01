from fastapi import APIRouter
from router.v1 import internship_router

api_router = APIRouter(
    prefix="/api/v1"
)

api_router.include_router(internship_router.router)