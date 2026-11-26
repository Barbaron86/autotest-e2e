from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import pytest

from clients.files.files_client import FilesClient
from clients.files.files_schema import CreateFileRequestSchema, CreateFileResponseSchema
from fixtures.resources import CreatedFileId, clean_owned_resource
from tools.assertions.files import assert_create_file_response


@dataclass(frozen=True)
class FileFixture:
    request: CreateFileRequestSchema
    response: CreateFileResponseSchema


@pytest.fixture
def cover_image() -> Path:
    """Возвращает путь к PNG, который используется как исходная обложка."""
    return Path(__file__).resolve().parents[1] / "testdata" / "files" / "cover.png"


@pytest.fixture
def function_file(files_client: FilesClient, cover_image: Path) -> Iterator[FileFixture]:
    """Загружает PNG под уникальным именем в тестовом аккаунте.

    Args:
        files_client: Клиент файлов тестового аккаунта.
        cover_image: Путь к изображению, содержимое которого отправляется в API.

    Yields:
        Запрос загрузки и проверенный ответ. После теста фикстура удаляет файл
        по ID или принимает 404, если его уже удалили вместе с курсом.
    """
    request = CreateFileRequestSchema(filename=f"cover-{uuid4().hex}.png", upload_file=cover_image)
    response = files_client.create_file_api(request)
    response.raise_for_status()
    file_id = CreatedFileId.model_validate_json(response.content).id
    with clean_owned_resource(file_id, files_client.delete_file_api):
        created = CreateFileResponseSchema.model_validate_json(response.content)
        assert_create_file_response(request, created)
        yield FileFixture(request, created)
