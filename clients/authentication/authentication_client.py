import allure
from httpx import Response

from clients.api_client import ApiClient
from clients.authentication.authentication_schema import LoginRequestSchema
from clients.public_http_builder import get_public_http_client
from tools.assertions.authentication import assert_login_response
from tools.routes import APIRoutes


class AuthenticationClient(ApiClient):
    def login_api(self, request: LoginRequestSchema) -> Response:
        """Отправляет модель входа и возвращает исходный HTTP-ответ."""
        with allure.step("Login request"):
            return self.post(f"{APIRoutes.AUTHENTICATION}/login", json=request.model_dump(mode="json"))

    def login_raw_api(self, payload: dict[str, object]) -> Response:
        """Отправляет payload входа без валидации моделью запроса.

        Args:
            payload: JSON-объект, включая намеренно невалидные поля негативного теста.

        Returns:
            Исходный HTTP-ответ, включая ошибочный статус.
        """
        with allure.step("Login raw request"):
            return self.post(f"{APIRoutes.AUTHENTICATION}/login", json=payload)

    def refresh_api(self) -> Response:
        """Обновляет сессию через cookie jar, отправляя POST без тела."""
        with allure.step("Refresh token request"):
            return self.post(f"{APIRoutes.AUTHENTICATION}/refresh")

    def logout_api(self) -> Response:
        """Завершает сессию через cookie jar, отправляя POST без тела."""
        with allure.step("Logout request"):
            return self.post(f"{APIRoutes.AUTHENTICATION}/logout")

    def login(self, request: LoginRequestSchema) -> Response:
        """Выполняет login и проверяет пустой ответ с cookies авторизации.

        Args:
            request: Email и пароль пользователя.

        Returns:
            Проверенный ответ HTTP 204. Cookies сохраняет HTTPX-клиент.

        Raises:
            httpx.HTTPStatusError: API вернул ошибочный статус.
            AssertionError: Статус, тело или cookies не соответствуют контракту.
        """
        with allure.step("Authenticate user"):
            response = self.login_api(request)
            response.raise_for_status()
            assert_login_response(response)
            return response


def get_authentication_client() -> AuthenticationClient:
    """Создаёт клиент авторизации с отдельным HTTPX-транспортом.

    Returns:
        Клиент авторизации. Вызывающий код закрывает его HTTPX-клиент.
    """
    return AuthenticationClient(client=get_public_http_client())
