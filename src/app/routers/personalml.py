from fastapi import Depends, APIRouter

from app.schemas.mlmodel import PersonalModelData, CreatePersonalModelData
from app.depends import validate_csv


api_router = APIRouter()


@api_router.post("/personal/models/new")
async def create_new_model(
    mlmodel_data: CreatePersonalModelData = Depends(),
    train_data: bytes = Depends(validate_csv),
):
    
    raise NotImplementedError


@api_router.post("/personal/models/use")
async def use_personal_model(mlmodel_data: PersonalModelData) -> PersonalModelData:
    
    raise NotImplementedError
