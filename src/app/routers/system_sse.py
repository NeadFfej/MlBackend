from fastapi import Body, APIRouter
from fastapi.exceptions import HTTPException

from core.sse.manager import ml_result_manager


api_router = APIRouter()


@api_router.post("/system/sse/newevent", include_in_schema=False)
async def create_event(
    user_id: str,
    data: str = Body(),
    event: str = "newdata",
    comment: str = None,
):
    context_manager = ml_result_manager.sse_managers.get(user_id)
    if not context_manager:
        raise HTTPException(404)

    await context_manager.create_event(
        event=event,
        data=data,
        comment=comment,
    )

    return {"status": "ok"}

