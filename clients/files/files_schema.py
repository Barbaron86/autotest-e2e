from pydantic import FilePath, HttpUrl

from clients.base_schema import BaseSchema


class FileSchema(BaseSchema):
    """Метаданные загруженного файла и адрес его содержимого."""

    id: str
    filename: str
    directory: str
    url: HttpUrl


class CreateFileRequestSchema(BaseSchema):
    """Метаданные и локальный путь файла для multipart-загрузки."""

    filename: str
    directory: str = "tests"
    upload_file: FilePath


class CreateFileResponseSchema(BaseSchema):
    """Ответ API с метаданными загруженного файла."""

    file: FileSchema


class GetFileResponseSchema(BaseSchema):
    """Ответ API с метаданными запрошенного файла."""

    file: FileSchema
