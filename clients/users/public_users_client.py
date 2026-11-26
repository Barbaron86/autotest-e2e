import allure
from httpx import Response

from clients.api_client import ApiClient
from clients.public_http_builder import get_public_http_client
from clients.users.user_schema import CreateUserRequestSchema, CreateUserResponseSchema
from tools.routes import APIRoutes


class PublicUsersClient(ApiClient):
    def create_user_api(self, request: CreateUserRequestSchema) -> Response:
        """Отправляет модель регистрации и возвращает исходный HTTP-ответ."""
        with allure.step("Register user request"):
            return self.post(APIRoutes.USERS, json=request.model_dump(mode="json"))

    def create_user(self, request: CreateUserRequestSchema) -> CreateUserResponseSchema:
        """Регистрирует пользователя и разбирает успешный ответ.

        Args:
            request: Учётные данные и имя нового пользователя.

        Returns:
            Модель ответа с зарегистрированным пользователем.

        Raises:
            httpx.HTTPStatusError: API вернул ошибочный статус.
            pydantic.ValidationError: Успешный ответ не соответствует схеме.
        """
        with allure.step("Register user"):
            response = self.create_user_api(request)
            response.raise_for_status()
            return CreateUserResponseSchema.model_validate_json(response.content)


def get_public_users_client() -> PublicUsersClient:
    """Создаёт клиент регистрации с отдельным HTTPX-транспортом.

    Returns:
        Публичный клиент пользователей. Вызывающий код закрывает его транспорт.
    """
    return PublicUsersClient(client=get_public_http_client())
