import allure
from httpx import Response

from clients.api_client import ApiClient
from clients.private_http_builder import AuthenticationUserSchema, get_private_http_client
from clients.users.user_schema import GetUserResponseSchema, UpdateUserRequestSchema
from tools.logger import log_model
from tools.routes import APIRoutes


class PrivateUsersClient(ApiClient):
    @allure.step("Get current user")
    def get_user_me_api(self) -> Response:
        """Запрашивает владельца текущей сессии и возвращает HTTP-ответ."""
        return self.get(f"{APIRoutes.USERS}/me")

    @allure.step("Get user request by ID {user_id}")
    def get_user_api(self, user_id: str) -> Response:
        """Запрашивает пользователя по UUID и возвращает HTTP-ответ."""
        return self.get(f"{APIRoutes.USERS}/{user_id}")

    @allure.step("Get user by ID {user_id}")
    def get_user(self, user_id: str) -> GetUserResponseSchema:
        """Получает пользователя по UUID из успешного ответа.

        Args:
            user_id: UUID запрашиваемого пользователя.

        Returns:
            Проверенная модель ответа с пользователем.

        Raises:
            httpx.HTTPStatusError: API вернул ошибочный статус.
            pydantic.ValidationError: Успешный ответ не соответствует схеме.
        """
        response = self.get_user_api(user_id)
        response.raise_for_status()
        result = GetUserResponseSchema.model_validate_json(response.content)
        log_model("Get user response", result)
        return result

    @allure.step("Delete user by ID {user_id}")
    def delete_user_api(self, user_id: str) -> Response:
        """Удаляет пользователя по UUID и возвращает исходный HTTP-ответ."""
        return self.delete(f"{APIRoutes.USERS}/{user_id}")

    @allure.step("Update user request")
    def update_user_api(self, user_id: str, request: UpdateUserRequestSchema) -> Response:
        """Отправляет явно заданные поля PATCH пользователя.

        Пропущенные поля исключаются из JSON. Явные значения null сохраняются
        и могут быть отклонены API согласно контракту конкретного поля.

        Args:
            user_id: UUID изменяемого пользователя.
            request: Частичное изменение данных пользователя.

        Returns:
            Исходный HTTP-ответ, включая ошибочный статус.
        """
        log_model("Update user request", request)
        return self.patch(f"{APIRoutes.USERS}/{user_id}", json=request.model_dump(mode="json", exclude_unset=True))


def get_private_users_client(user: AuthenticationUserSchema) -> PrivateUsersClient:
    """Выполняет login и создаёт приватный клиент пользователей.

    Args:
        user: Учётные данные владельца сессии.

    Returns:
        Клиент пользователей с отдельным авторизованным транспортом.
        Вызывающий код отвечает за закрытие транспорта.
    """
    return PrivateUsersClient(client=get_private_http_client(user))
