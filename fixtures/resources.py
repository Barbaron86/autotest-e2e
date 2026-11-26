from collections.abc import Callable, Iterator
from contextlib import contextmanager
from http import HTTPStatus

from httpx import Response
from pydantic import AliasPath, Field

from clients.base_schema import BaseSchema


class CreatedCourseId(BaseSchema):
    """Идентификатор созданного курса для регистрации очистки."""

    id: str = Field(strict=True, validation_alias=AliasPath("course", "id"))


class CreatedFileId(BaseSchema):
    """Идентификатор загруженного файла для регистрации очистки."""

    id: str = Field(strict=True, validation_alias=AliasPath("file", "id"))


class CreatedUserId(BaseSchema):
    """Идентификатор нового пользователя для регистрации очистки."""

    id: str = Field(strict=True, validation_alias=AliasPath("user", "id"))


def delete_owned_resource(resource_id: str, delete: Callable[[str], Response]) -> None:
    """Удаляет тестовый ресурс по ID и принимает 404 при повторной очистке.

    Args:
        resource_id: Идентификатор ресурса, созданного текущим тестом.
        delete: Метод клиента, отправляющий DELETE для указанного ID.

    Raises:
        HTTPStatusError: Если сервер ответил статусом вне 2xx, кроме 404.
    """
    response = delete(resource_id)
    if response.status_code != HTTPStatus.NOT_FOUND:
        response.raise_for_status()


@contextmanager
def clean_owned_resource(resource_id: str, delete: Callable[[str], Response]) -> Iterator[None]:
    """Удаляет ресурс при выходе из контекста, включая выход с исключением.

    Args:
        resource_id: Идентификатор ресурса, созданного текущим тестом.
        delete: Метод клиента, которому передаётся ID для удаления.
    """
    try:
        yield
    finally:
        delete_owned_resource(resource_id, delete)
