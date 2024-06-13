from fastapi import APIRouter

from .publickml import api_router as __pub_ml_router
from .personalml import api_router as __per_ml_router

api_router = APIRouter()
api_router.include_router(__pub_ml_router, prefix="/ml", tags=["pub_mlmodel"])
api_router.include_router(__per_ml_router, prefix="/ml", tags=["per_mlmodel"])
