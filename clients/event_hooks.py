from httpx import Request, Response
from loguru import logger

logger = logger.bind(component="HTTP", diagnostic_safe=True)


def log_request_event_hook(request: Request) -> None:
    """Записывает метод и путь запроса без заголовков и тела."""
    logger.info(f"→ {request.method} {request.url.path}")


def log_response_event_hook(response: Response) -> None:
    """Записывает статус, метод и путь ответа без его тела."""
    logger.info(
        f"← {response.status_code} {response.reason_phrase} {response.request.method} {response.request.url.path}"
    )
