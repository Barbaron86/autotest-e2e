from httpx import Client

from clients.event_hooks import log_request_event_hook, log_response_event_hook
from config import settings


def get_public_http_client() -> Client:
    """Создаёт HTTPX-клиент с безопасными HTTP-логами.

    Returns:
        Открытый клиент. Вызывающий код отвечает за его закрытие.
    """
    return Client(
        base_url=str(settings.api_base_url),
        timeout=settings.api_timeout,
        headers={"Origin": settings.api_origin},
        event_hooks={"request": [log_request_event_hook], "response": [log_response_event_hook]},
    )
