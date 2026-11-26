from httpx import Client
from pydantic import EmailStr, Field

from clients.authentication.authentication_client import get_authentication_client
from clients.authentication.authentication_schema import LoginRequestSchema, TokenSchema
from clients.base_schema import BaseSchema
from clients.public_http_builder import get_public_http_client


class AuthenticationUserSchema(BaseSchema):
    """Учётные данные тестового аккаунта для входа через API."""

    email: EmailStr
    password: str = Field(repr=False)


def get_authorized_http_client(token: TokenSchema) -> Client:
    """Создаёт клиент с Bearer-заголовком переданного access-токена.

    Args:
        token: Полученная пара токенов авторизации.

    Returns:
        Открытый HTTPX-клиент. Его закрывает вызывающий код.
    """
    client = get_public_http_client()
    client.headers["Authorization"] = f"Bearer {token.access_token}"
    return client


def get_private_http_client(user: AuthenticationUserSchema) -> Client:
    """Входит через API и создаёт авторизованный клиент.

    Временный клиент входа закрывается до возврата результата.
    Каждый вызов выполняет отдельный login.

    Args:
        user: Email и пароль тестового пользователя.

    Returns:
        Открытый клиент с полученным access-токеном. Его закрывает вызывающий код.

    Raises:
        httpx.HTTPStatusError: API входа вернул ошибочный статус.
        pydantic.ValidationError: Успешный ответ входа не соответствует схеме.
    """
    authentication_client = get_authentication_client()
    with authentication_client.client:
        login = authentication_client.login(LoginRequestSchema(email=user.email, password=user.password))

    return get_authorized_http_client(login.token)
