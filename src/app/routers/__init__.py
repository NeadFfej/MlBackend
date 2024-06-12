from fastapi import APIRouter

from .mlmodel import api_router as __ml_router


api_router = APIRouter()
api_router.include_router(__ml_router, prefix="/ml", tags=["mlmodel"])
