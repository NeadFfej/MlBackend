from fastapi import Depends, File, Form, APIRouter, UploadFile
from fastapi.exceptions import HTTPException

from app.schemas.mlmodel import PublickModelData, PersonalModelData, CreatePublickModelData, CreatePersonalModelData


api_router = APIRouter()


def __validate_csv(file: UploadFile):
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="Uploaded file must be a CSV file")
    
    return file.file.read()


@api_router.post("/publick/models/new")
async def create_new_model(
    mlmodel_data: CreatePublickModelData = Depends(),
    train_data: bytes = Depends(__validate_csv),
):
    
    return mlmodel_data


@api_router.get("/publick/models/use")
async def use_publick_model(mlmodel_data: PublickModelData):
    
    return mlmodel_data


@api_router.post("/personal/models/new")
async def create_new_model(
    mlmodel_data: CreatePersonalModelData = Depends(),
    train_data: bytes = Depends(__validate_csv),
):
    
    return mlmodel_data


@api_router.get("/personal/models/use")
async def use_publick_model(mlmodel_data: PersonalModelData):
    
    return mlmodel_data
