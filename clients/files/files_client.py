from mimetypes import guess_type

import allure
from httpx import Response

from clients.api_client import ApiClient
from clients.files.files_schema import CreateFileRequestSchema, CreateFileResponseSchema
from clients.private_http_builder import AuthenticationUserSchema, get_private_http_client
from tools.logger import log_model
from tools.routes import APIRoutes


class FilesClient(ApiClient):
    @allure.step("Upload file request")
    def create_file_api(self, request: CreateFileRequestSchema) -> Response:
        """Загружает локальный файл multipart-запросом.

        Файл открывается только на время отправки и закрывается перед возвратом.
        MIME-тип определяется по имени, при неизвестном расширении используется
        application/octet-stream.

        Args:
            request: Путь к локальному файлу и метаданные загрузки.

        Returns:
            Исходный HTTP-ответ, включая ошибочный статус.

        Raises:
            OSError: Локальный файл не удалось открыть или прочитать.
        """
        log_model("Create file request", request)
        content_type = guess_type(request.upload_file.name)[0] or "application/octet-stream"
        with request.upload_file.open("rb") as upload_file:
            return self.post(
                APIRoutes.FILES,
                data={"filename": request.filename, "directory": request.directory},
                files={"upload_file": (request.upload_file.name, upload_file, content_type)},
            )

    @allure.step("Create file")
    def create_file(self, request: CreateFileRequestSchema) -> CreateFileResponseSchema:
        """Загружает файл и разбирает успешный ответ.

        Args:
            request: Локальный файл и метаданные загрузки.

        Returns:
            Модель ответа с метаданными созданного файла.

        Raises:
            OSError: Локальный файл недоступен для чтения.
            httpx.HTTPStatusError: API вернул ошибочный статус.
            pydantic.ValidationError: Успешный ответ не соответствует схеме.
        """
        response = self.create_file_api(request)
        response.raise_for_status()
        result = CreateFileResponseSchema.model_validate_json(response.content)
        log_model("Create file response", result)
        return result

    @allure.step("Get file metadata by ID {file_id}")
    def get_file_api(self, file_id: str) -> Response:
        """Запрашивает метаданные файла по UUID и возвращает HTTP-ответ."""
        return self.get(f"{APIRoutes.FILES}/{file_id}")

    @allure.step("Get file content by ID {file_id}")
    def get_file_content_api(self, file_id: str) -> Response:
        """Запрашивает байты файла по UUID и возвращает HTTP-ответ."""
        return self.get(f"{APIRoutes.FILES}/{file_id}/content")

    @allure.step("Delete file by ID {file_id}")
    def delete_file_api(self, file_id: str) -> Response:
        """Удаляет файл по UUID и возвращает исходный HTTP-ответ."""
        return self.delete(f"{APIRoutes.FILES}/{file_id}")


def get_files_client(user: AuthenticationUserSchema) -> FilesClient:
    """Выполняет login и создаёт API-клиент файлов.

    Args:
        user: Учётные данные владельца сессии.

    Returns:
        Клиент файлов с отдельным авторизованным транспортом.
        Вызывающий код отвечает за закрытие транспорта.
    """
    return FilesClient(client=get_private_http_client(user))
