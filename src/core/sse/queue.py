from typing import Optional
import asyncio

from core.utils.system import AppStatus
from core.configuration import settings
from core.redis.client import get_redis_client


class SseQueue:
    def __init__(self, user_id) -> None:
        self._user_id = user_id
        self._queue = 'sse_queue:' + user_id
        self._ping_task = asyncio.create_task(self.ping())

    def __del__(self):
        self._ping_task.cancel()

    def __get_event_text(self, **sse_event) -> str:
        string_event = ""
        for key, value in sse_event.items():
            if not value:
                continue

            if key == "comment":
                string_event += f": {value}"
                continue

            string_event += f"{key}: {value}\n"

        if string_event.count(":") == 0:
            raise ValueError

        return string_event + "\n\n"

    async def create_event(
        self,
        event: Optional[str] = None,
        data: Optional[str] = None,
        id: Optional[int] = None,
        retry: Optional[int] = None,
        comment: Optional[str] = None,
    ) -> None:
        """
        event - Строка, идентифицирующая тип описанного события.
            Если event указан, то событие будет отправлено в браузер
            обработчику указанного имени события. Исходный код сайта
            должен использовать addEventListener() для обработки именованных
            событий. Обработчик onmessage вызывается, если для сообщения
            не указано имя события.

        data - Поле данных для сообщения. Когда EventSource получает несколько
            последовательных строк, начинающихся с data:, он объединяет их, вставляя
            символ новой строки между каждой из них. Последние переводы строки удаляются.

        id - Идентификатор события для установки значения последнего ID события для объекта EventSource.

        retry - Время переподключения, используемое при попытке отправить событие.
            Это должно быть целое число, указывающее время переподключения в миллисекундах.
            Если указано нецелое значение, поле игнорируется.
        """
        sse_event_text = self.__get_event_text(
            **{
                "event": event,
                "data": data,
                "id": id,
                "retry": retry,
                "comment": comment,
            }
        )
        async with get_redis_client() as client:
            await client.rpush(self._queue, sse_event_text)

    async def get_event(self) -> str:
        async with get_redis_client() as client:
            event = await client.blpop(self._queue)
            return event[1]

    async def ping(self):
        while True:
            await self.create_event(comment="ping")
            await asyncio.sleep(15)

    async def get_events(self):
        while AppStatus.should_exit is False:
            try:
                event = await asyncio.wait_for(
                    self.get_event(),
                    timeout=1 if settings.ENVIRONMENT == "local" else 10,
                )
                yield event
            # Вероятно не лучшее решение, но пока пусть будет так.
            except asyncio.TimeoutError:
                pass

        if settings.ENVIRONMENT == "local":
            d = self.__get_event_text(
                **{
                    "event": "system",
                    "data": "service restart",
                    "id": None,
                    "retry": None,
                    "comment": "service restarting at the moment",
                }
            )
            yield d.replace("\n\n", "\r\n")
