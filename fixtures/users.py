from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from httpx import Client

from clients.private_http_builder import AuthenticationUserSchema, get_private_http_client
from clients.users.private_users_client import PrivateUsersClient
from clients.users.public_users_client import PublicUsersClient
from clients.users.user_schema import CreateUserRequestSchema, CreateUserResponseSchema
from fixtures.resources import CreatedUserId, delete_owned_resource
from testdata.factories import generate_user_request
from tools.assertions.users import assert_create_user_response


@dataclass(frozen=True)
class UserFixture:
    request: CreateUserRequestSchema
    response: CreateUserResponseSchema

    @property
    def authentication_user(self) -> AuthenticationUserSchema:
        """Возвращает данные регистрации в формате клиента аутентификации."""
        return AuthenticationUserSchema(email=self.request.email, password=self.request.password)


@dataclass(frozen=True)
class AuthenticatedAccount:
    """Тестовый пользователь и его отдельная API-сессия с Cookie Jar."""

    user: UserFixture
    client: Client


@pytest.fixture
def authenticated_account(public_users_client: PublicUsersClient) -> Iterator[AuthenticatedAccount]:
    """Создаёт отдельный аккаунт и сессию для одного теста.

    При завершении удаляет аккаунт и закрывает HTTP-клиент. Если начальный
    вход не удался, для удаления выполняет повторную аутентификацию.

    Args:
        public_users_client: Клиент, регистрирующий отдельный тестовый аккаунт.

    Yields:
        Проверенные данные пользователя и его HTTP-клиент с собственной
        серверной сессией. Браузер входит в этот аккаунт независимо.
    """
    create_request = generate_user_request()
    create_response = public_users_client.create_user_api(create_request)
    create_response.raise_for_status()
    user_id = CreatedUserId.model_validate_json(create_response.content).id
    credentials = AuthenticationUserSchema(email=create_request.email, password=create_request.password)

    client = None
    try:
        client = get_private_http_client(credentials)
        user = CreateUserResponseSchema.model_validate_json(create_response.content)
        assert_create_user_response(create_request, user)
        yield AuthenticatedAccount(UserFixture(create_request, user), client)
    finally:
        # При сбое начального входа создаём отдельную сессию для очистки аккаунта.
        cleanup_client = get_private_http_client(credentials) if client is None else client
        try:
            delete_owned_resource(user_id, PrivateUsersClient(cleanup_client).delete_user_api)
        finally:
            cleanup_client.close()


@pytest.fixture
def function_user(authenticated_account: AuthenticatedAccount) -> UserFixture:
    """Предоставляет запрос регистрации и ответ с ID тестового аккаунта."""
    return authenticated_account.user


@pytest.fixture
def authenticated_http_client(authenticated_account: AuthenticatedAccount) -> Client:
    """Предоставляет доменным клиентам теста общий транспорт с Cookie Jar."""
    return authenticated_account.client
