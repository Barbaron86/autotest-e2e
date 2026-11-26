from collections.abc import Iterator

import pytest
from httpx import Client

from clients.authentication.authentication_client import AuthenticationClient
from clients.courses.courses_client import CoursesClient
from clients.exercises.exercises_client import ExercisesClient
from clients.files.files_client import FilesClient
from clients.public_http_builder import get_public_http_client
from clients.users.private_users_client import PrivateUsersClient
from clients.users.public_users_client import PublicUsersClient


@pytest.fixture
def public_http_client() -> Iterator[Client]:
    """Предоставляет HTTP-клиент без токена и закрывает его после теста."""
    with get_public_http_client() as client:
        yield client


@pytest.fixture
def authentication_client(public_http_client: Client) -> AuthenticationClient:
    """Создаёт клиент входа и обновления токенов поверх публичного транспорта."""
    return AuthenticationClient(public_http_client)


@pytest.fixture
def public_users_client(public_http_client: Client) -> PublicUsersClient:
    """Создаёт клиент регистрации поверх публичного транспорта."""
    return PublicUsersClient(public_http_client)


@pytest.fixture
def private_users_client(authenticated_http_client: Client) -> PrivateUsersClient:
    """Создаёт клиент профиля поверх авторизованного транспорта теста."""
    return PrivateUsersClient(authenticated_http_client)


@pytest.fixture
def files_client(authenticated_http_client: Client) -> FilesClient:
    """Создаёт клиент файлов от имени тестового аккаунта."""
    return FilesClient(authenticated_http_client)


@pytest.fixture
def courses_client(authenticated_http_client: Client) -> CoursesClient:
    """Создаёт клиент курсов от имени тестового аккаунта."""
    return CoursesClient(authenticated_http_client)


@pytest.fixture
def exercises_client(authenticated_http_client: Client) -> ExercisesClient:
    """Создаёт клиент упражнений от имени тестового аккаунта."""
    return ExercisesClient(authenticated_http_client)
