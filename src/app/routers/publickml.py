from fastapi import Depends, Query, APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from celery.result import AsyncResult

from app.schemas.mlmodel import PublickModelData, CreatePublickModelData
from app.depends import validate_csv, get_session_validator
from app.tasks.publickml import check_ml
from core.security.tokens import create_jwt_token
from core.sse.manager import ml_result_manager, TextEventStreamResponse


api_router = APIRouter()
validate_session = get_session_validator()


@api_router.post("/publick/models/new", include_in_schema=False)
async def create_new_model(
    mlmodel_data: CreatePublickModelData = Depends(),
    train_data: bytes = Depends(validate_csv),
):
    
    raise NotImplementedError


@api_router.get("/publick/models/use", status_code=201)
async def use_publick_model(
    token_data = Depends(validate_session),
    text_request: str = Query(min_length=10, max_length=10000),
    mlmodel_data: PublickModelData = Depends(PublickModelData)
):
    """
    Для просмотра результа лучше откройте sse соединение (ендпоинт ниже)
    """
    need_token = False
    if not token_data:
        need_token = True
        token, token_data = create_jwt_token(need_token_data=True)
        
    task = check_ml.delay(token_data["session"], text_request, mlmodel_data.model_dump())
    response = JSONResponse({"is_task_started": True, "task_id": task.id}, status_code=201)
    if need_token:
        response.set_cookie("access", token)
        
    return response


@api_router.get("/publick/models/getresult/final")
async def get_task_result(task_id: str):
    async_result = AsyncResult(task_id)
    return async_result.result


@api_router.get("/publick/models/getresult/stream", response_class=TextEventStreamResponse)
async def get_task_result(sse_response = Depends(ml_result_manager)) -> StreamingResponse:
    """
    К сожалению Swagger не имеет поддержки моментального отображения <mark>text/event-stream</mark> <br>
    Для получения результата [`нажми на меня`](/ml/publick/models/getresult/stream)
    """
    return sse_response