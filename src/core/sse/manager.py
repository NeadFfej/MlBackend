from dataclasses import dataclass
from uuid import uuid4

from fastapi.responses import StreamingResponse
from fastapi import Depends, BackgroundTasks, Response

from core.sse.queue import SseQueue
from core.security.tokens import create_jwt_token
from core.configuration import settings
from app.depends import get_session_validator


validate_session = get_session_validator()


class TextEventStreamResponse(Response):
    media_type = 'text/event-stream'


@dataclass
class SseManagerContext:
    listeners: dict[str, SseQueue]

    @staticmethod
    def get_new_manager() -> "SseManagerContext":
        return SseManagerContext({})

    def create_listener(self):
        user_uuid = uuid4().hex
        self.listeners[user_uuid] = SseQueue(user_uuid)
        return user_uuid

    def delete_listener(self, user_uuid: str):
        del self.listeners[user_uuid]

    def get_listener(self, user_uuid: str) -> SseQueue:
        return self.listeners.get(user_uuid)

    async def create_event(self, **event_data):
        """
        event: Optional[str] = None,
        data: Optional[str] = None,
        id: Optional[int] = None,
        retry: Optional[int] = None,
        comment: Optional[str] = None,
        """
        for listener in self.listeners.values():
            await listener.create_event(**event_data)


class BaseNotificationManager:
    # Данная реализация не будет адекватно работать при нескольких воркерах!
    def __init__(self) -> None:
        self.sse_managers: dict[int, SseManagerContext] = {}

    async def __call__(
        self,
        token_data = Depends(validate_session),
    ) -> StreamingResponse:
        need_token = False
        if not token_data:
            need_token = True
            token, token_data = create_jwt_token(need_token_data=True)
        
        sse_response = await self.add_user(token_data["session"])
        if need_token:
            sse_response.set_cookie("access", token)
        
        return sse_response

    async def add_user(self, user_id: int) -> StreamingResponse:
        context = self.sse_managers.get(user_id)
        if not context:
            context = SseManagerContext.get_new_manager()

        user_uuid = context.create_listener()
        self.sse_managers[user_id] = context

        if settings.ENVIRONMENT == "local":
            await context.create_event(
                event="system",
                data=f"connected - {user_uuid}\n"\
                    f"connected len: {len(context.listeners)}\n"\
                    f"members len: {len(self.sse_managers)}",
                comment="base message for create new connection",
            )

        return self.get_sse_response(user_id, user_uuid)

    def get_sse_response(self, user_id: int, user_uuid: str) -> StreamingResponse:
        context = self.sse_managers[user_id]
        listener = context.get_listener(user_uuid)

        bg_tasks = BackgroundTasks()
        bg_tasks.add_task(context.delete_listener, user_uuid)
        response = StreamingResponse(
            content=listener.get_events(),
            media_type="text/event-stream",
            background=bg_tasks,
        )
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Connection"] = "keep-alive"

        return response


ml_result_manager = BaseNotificationManager() 
