from fastapi import Depends, Query, APIRouter
from celery.result import AsyncResult

from app.schemas.mlmodel import PublickModelData, CreatePublickModelData
from app.depends import validate_csv
from app.tasks.publickml import check_ml

api_router = APIRouter()


@api_router.post("/publick/models/new")
async def create_new_model(
    mlmodel_data: CreatePublickModelData = Depends(),
    train_data: bytes = Depends(validate_csv),
):
    
    raise NotImplementedError


@api_router.get("/publick/models/use", status_code=201)
async def use_publick_model(
    text_request: str = Query(min_length=10, max_length=10000),
    mlmodel_data: PublickModelData = Depends(PublickModelData.query_validator)
):
    # Предполагается, что будет использоваться sse для моделей
    task = check_ml.delay(mlmodel_data.model_dump())
    return {"task_id": task.id}


@api_router.get("/publick/models/get_result", status_code=200)
async def get_task_result(task_id: str):
    task_result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }