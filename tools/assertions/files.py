from urllib.parse import urlsplit

import allure

from clients.error_schema import InternalErrorResponseSchema, ValidationErrorResponseSchema
from clients.files.files_schema import (
    CreateFileRequestSchema,
    CreateFileResponseSchema,
    FileSchema,
    GetFileResponseSchema,
)
from tools.assertions.base import assert_equal
from tools.assertions.errors import (
    ValidationErrorExpectation,
    assert_internal_error_response,
    assert_invalid_uuid_response,
    assert_validation_error_response,
)
from tools.error_messages import ApiErrorMessage
from tools.error_types import ValidationErrorType
from tools.logger import log_model
from tools.routes import APIRoutes


@allure.step("Check create file response")
def assert_create_file_response(request: CreateFileRequestSchema, response: CreateFileResponseSchema) -> None:
    """Проверяет подписи файла и защищённый маршрут его содержимого.

    Args:
        request: Данные загрузки с ожидаемыми именем и директорией.
        response: Ответ API на загрузку файла.

    Raises:
        AssertionError: Если имя, директория или абсолютный URL содержимого
            не совпадают с ожиданиями либо URL содержит query или fragment.
    """
    log_model("Expected file request", request)
    log_model("Actual create file response", response)
    url = urlsplit(str(response.file.url))
    assert url.scheme in ("http", "https") and url.netloc, "File URL must be absolute."
    assert_equal(url.path, f"{APIRoutes.FILES}/{response.file.id}/content", "url path")
    assert not url.query and (not url.fragment), "File URL must reference the authenticated content route."
    assert_equal(response.file.filename, request.filename, "filename")
    assert_equal(response.file.directory, request.directory, "directory")


@allure.step("Check file")
def assert_file(actual: FileSchema, expected: FileSchema) -> None:
    """Проверяет соответствие фактических данных файла ожидаемым.

    Args:
        actual: Фактические данные файла из ответа API.
        expected: Ожидаемые данные файла.

    Raises:
        AssertionError: Если идентификатор, URL, имя файла
            или директория не соответствуют ожидаемым значениям.
    """
    log_model("Actual file", actual)
    log_model("Expected file", expected)
    assert_equal(actual.id, expected.id, "id")
    assert_equal(actual.url, expected.url, "url")
    assert_equal(actual.filename, expected.filename, "filename")
    assert_equal(actual.directory, expected.directory, "directory")


@allure.step("Check get file response")
def assert_get_file_response(
    get_file_response: GetFileResponseSchema, create_file_response: CreateFileResponseSchema
) -> None:
    """Проверяет ответ получения файла по данным его создания.

    Args:
        get_file_response: Ответ API на запрос получения файла.
        create_file_response: Ответ API, полученный при создании файла.

    Raises:
        AssertionError: Если данные полученного файла
            не соответствуют данным созданного файла.
    """
    assert_file(get_file_response.file, create_file_response.file)


def assert_create_file_with_empty_filename_response(actual: ValidationErrorResponseSchema) -> None:
    """Проверяет ошибку валидации при загрузке файла с пустым именем.

    Args:
        actual: Фактический ответ API с ошибками валидации.

    Raises:
        AssertionError: Если ответ не соответствует ошибке пустого имени файла.
    """
    with allure.step("Check create file with empty filename response"):
        expected = [
            ValidationErrorExpectation(
                type=ValidationErrorType.STRING_TOO_SHORT,
                input="",
                context={"min_length": 1},
                location=["body", "filename"],
            )
        ]
        assert_validation_error_response(actual=actual, expected=expected)


def assert_create_file_with_too_long_filename_response(actual: ValidationErrorResponseSchema, filename: str) -> None:
    """Проверяет ошибку превышения допустимой длины имени файла.

    Args:
        actual: Фактический ответ API с ошибками валидации.
        filename: Имя файла, переданное в запросе на загрузку.

    Raises:
        AssertionError: Если ответ не соответствует ограничению длины
            имени файла в 250 символов или содержит другой входной параметр.
    """
    with allure.step("Check create file with too long filename response"):
        expected = [
            ValidationErrorExpectation(
                type=ValidationErrorType.STRING_TOO_LONG,
                input=filename,
                context={"max_length": 250},
                location=["body", "filename"],
            )
        ]
        assert_validation_error_response(actual=actual, expected=expected)


def assert_create_file_with_empty_directory_response(actual: ValidationErrorResponseSchema) -> None:
    """Проверяет ошибку валидации при загрузке файла с пустой директорией.

    Args:
        actual: Фактический ответ API с ошибками валидации.

    Raises:
        AssertionError: Если ответ не соответствует ошибке пустой директории.
    """
    with allure.step("Check create file with empty directory response"):
        expected = [
            ValidationErrorExpectation(
                type=ValidationErrorType.STRING_TOO_SHORT,
                input="",
                context={"min_length": 1},
                location=["body", "directory"],
            )
        ]
        assert_validation_error_response(actual=actual, expected=expected)


def assert_file_not_found_response(actual: InternalErrorResponseSchema) -> None:
    """Проверяет сообщение API об отсутствии файла.

    Args:
        actual: Фактический ответ API с сообщением об ошибке.

    Raises:
        AssertionError: Если ответ не содержит сообщение «File not found».
    """
    with allure.step("Check file not found response"):
        expected = InternalErrorResponseSchema(detail=ApiErrorMessage.FILE_NOT_FOUND)
        assert_internal_error_response(actual=actual, expected=expected)


def assert_file_with_invalid_id_response(actual: ValidationErrorResponseSchema, file_id: str) -> None:
    """Проверяет ошибку валидации некорректного UUID файла.

    Args:
        actual: Фактический ответ API с ошибками валидации.
        file_id: Некорректный UUID файла, переданный в path-параметре.

    Raises:
        AssertionError: Если количество, тип, расположение или входное
            значение ошибки не соответствуют ожидаемым.
    """
    with allure.step("Check file with invalid ID response"):
        assert_invalid_uuid_response(actual=actual, invalid_id=file_id, location=["path", "file_id"])
