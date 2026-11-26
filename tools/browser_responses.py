from urllib.parse import urlsplit

from playwright.sync_api import Response


def matches_api_response(response: Response, method: str, path: str) -> bool:
    """Сопоставляет HTTP-метод и путь ответа браузера с API-маршрутом.

    Args:
        response: Наблюдаемый браузерный ответ.
        method: Ожидаемый HTTP-метод в том же регистре.
        path: Полный путь API, включая префикс /api/v1.

    Returns:
        True при совпадении метода и пути. Origin и query не сравниваются.
    """
    return response.request.method == method and urlsplit(response.url).path == path
