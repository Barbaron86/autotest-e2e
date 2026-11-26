import allure
from httpx import Response

from clients.api_client import ApiClient
from clients.authentication.authentication_schema import LoginRequestSchema, LoginResponseSchema, RefreshRequestSchema
from clients.public_http_builder import get_public_http_client
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

    def refresh_api(self, request: RefreshRequestSchema) -> Response:
        """Отправляет refresh-токен из модели и возвращает HTTP-ответ."""
        with allure.step("Refresh token request"):
            return self.post(f"{APIRoutes.AUTHENTICATION}/refresh", json=request.model_dump(mode="json"))

    def refresh_raw_api(self, payload: dict[str, object]) -> Response:
        """Отправляет payload обновления токенов без валидации моделью.

        Args:
            payload: JSON-объект, включая невалидные значения для негативных проверок.

        Returns:
            Исходный HTTP-ответ, включая ошибочный статус.
        """
        with allure.step("Refresh raw request"):
            return self.post(f"{APIRoutes.AUTHENTICATION}/refresh", json=payload)

    def login(self, request: LoginRequestSchema) -> LoginResponseSchema:
        """Выполняет login и разбирает успешный ответ с токенами.

        Args:
            request: Email и пароль пользователя.

        Returns:
            Проверенная модель ответа авторизации.

        Raises:
            httpx.HTTPStatusError: API вернул ошибочный статус.
            pydantic.ValidationError: Успешный ответ не соответствует схеме.
        """
        with allure.step("Authenticate user"):
            response = self.login_api(request)
            response.raise_for_status()
            return LoginResponseSchema.model_validate_json(response.content)


def get_authentication_client() -> AuthenticationClient:
    """Создаёт клиент авторизации с отдельным HTTPX-транспортом.

    Returns:
        Клиент авторизации. Вызывающий код закрывает его HTTPX-клиент.
    """
    return AuthenticationClient(client=get_public_http_client())
