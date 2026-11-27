from httpx import Client
from pydantic import EmailStr, Field

from clients.authentication.authentication_client import get_authentication_client
from clients.authentication.authentication_schema import LoginRequestSchema
from clients.base_schema import BaseSchema


class AuthenticationUserSchema(BaseSchema):
    """Учётные данные тестового аккаунта для входа через API."""

    email: EmailStr
    password: str = Field(repr=False)


def get_private_http_client(user: AuthenticationUserSchema) -> Client:
    """Возвращает HTTPX-клиент с cookies независимого входа пользователя.

    Каждый вызов выполняет отдельный login и сохраняет cookie jar в том же
    клиенте. При ошибке входа транспорт закрывается.

    Args:
        user: Email и пароль тестового пользователя.

    Returns:
        Открытый клиент с собственной сессией. Его закрывает вызывающий код.

    Raises:
        httpx.HTTPStatusError: API входа вернул ошибочный статус.
        AssertionError: Успешный ответ входа не соответствует контракту.
    """
    authentication_client = get_authentication_client()
    try:
        authentication_client.login(LoginRequestSchema(email=user.email, password=user.password))
    except BaseException:
        authentication_client.client.close()
        raise
    return authentication_client.client
