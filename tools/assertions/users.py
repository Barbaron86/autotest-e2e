from re import fullmatch

import allure

from clients.error_schema import InternalErrorResponseSchema, ValidationErrorResponseSchema
from clients.users.user_schema import (
    CreateUserRequestSchema,
    CreateUserResponseSchema,
    GetUserResponseSchema,
    UpdateUserRequestSchema,
    UpdateUserResponseSchema,
    UserSchema,
)
from tools.assertions.base import assert_equal
from tools.assertions.errors import (
    ValidationErrorExpectation,
    assert_internal_error_response,
    assert_invalid_uuid_response,
    assert_validation_error_response,
)
from tools.error_messages import ApiErrorMessage, ApiErrorPattern
from tools.error_types import ValidationErrorType
from tools.logger import log_model


def assert_user_with_existing_email_response(actual: InternalErrorResponseSchema, email: str) -> None:
    """Проверяет причину отказа и email, извлечённый из сообщения API."""
    with allure.step("Check user with existing email response"):
        match = fullmatch(ApiErrorPattern.USER_ALREADY_EXISTS, actual.detail)
        assert match is not None, "Expected a user-with-existing-email rejection"
        assert_equal(match["email"], email, name="existing email")


def assert_create_user_response(request: CreateUserRequestSchema, response: CreateUserResponseSchema) -> None:
    """Проверяет данные созданного пользователя в ответе API.

    Сравнивает данные пользователя из ответа API
    с данными, переданными в запросе на создание пользователя.

    Args:
        request: Данные запроса на создание пользователя.
        response: Ответ API с данными созданного пользователя.

    Raises:
        AssertionError: Если данные пользователя в ответе
            не совпадают с данными запроса.
    """
    with allure.step("Check create user response"):
        log_model("Actual create user response", response)
        assert_equal(response.user.email, request.email, "Email")
        assert_equal(response.user.first_name, request.first_name, "First name")
        assert_equal(response.user.last_name, request.last_name, "Last name")
        assert_equal(response.user.middle_name, request.middle_name, "Middle name")


@allure.step("Check user")
def assert_user(actual: UserSchema, expected: UserSchema) -> None:
    """Проверяет совпадение данных пользователя.

    Сравнивает идентификатор, email, фамилию, имя и отчество.

    Args:
        actual: Фактические данные пользователя.
        expected: Ожидаемые данные пользователя.

    Raises:
        AssertionError: Если хотя бы одно поле пользователя не совпадает.
    """
    log_model("Actual user", actual)
    log_model("Expected user", expected)
    assert_equal(actual.id, expected.id, "ID")
    assert_equal(actual.email, expected.email, "Email")
    assert_equal(actual.last_name, expected.last_name, "Last name")
    assert_equal(actual.first_name, expected.first_name, "First name")
    assert_equal(actual.middle_name, expected.middle_name, "Middle name")


@allure.step("Check get user response")
def assert_get_user_response(
    get_user_response: GetUserResponseSchema, create_user_response: CreateUserResponseSchema
) -> None:
    """Проверяет данные пользователя в ответе на запрос получения.

    Сравнивает полученного пользователя с данными ответа на создание.

    Args:
        get_user_response: Ответ API на запрос получения пользователя.
        create_user_response: Ответ API на запрос создания пользователя.

    Raises:
        AssertionError: Если данные полученного пользователя
            не совпадают с данными созданного пользователя.
    """
    assert_user(actual=get_user_response.user, expected=create_user_response.user)


def assert_user_not_found_response(actual: InternalErrorResponseSchema) -> None:
    """Проверяет сообщение API об отсутствии пользователя.

    Args:
        actual: Фактический ответ API с сообщением об ошибке.

    Raises:
        AssertionError: Если сообщение не соответствует ошибке отсутствия пользователя.
    """
    with allure.step("Check user not found response"):
        expected = InternalErrorResponseSchema(detail=ApiErrorMessage.USER_NOT_FOUND)
        assert_internal_error_response(actual=actual, expected=expected)


@allure.step("Check update user response")
def assert_update_user_response(
    request: UpdateUserRequestSchema, response: UpdateUserResponseSchema, original_user: UserSchema
) -> None:
    """Проверяет изменённые и сохранённые поля пользователя после PATCH.

    Args:
        request: Запрос частичного обновления пользователя.
        response: Ответ API после обновления.
        original_user: Исходные данные пользователя для проверки полей,
            отсутствовавших в запросе.

    Raises:
        AssertionError: Если обновлённые поля отличаются от запроса
            или остальные данные пользователя изменились.
    """
    log_model("Expected user update", request)
    expected_user = original_user.model_copy(update=request.model_dump(exclude_unset=True, by_alias=False))
    assert_user(actual=response.user, expected=expected_user)


def assert_user_with_invalid_id_response(actual: ValidationErrorResponseSchema, user_id: str) -> None:
    """Проверяет ошибку валидации некорректного UUID пользователя.

    Args:
        actual: Фактический ответ API с ошибками валидации.
        user_id: Некорректный UUID пользователя в path-параметре.

    Raises:
        AssertionError: Если данные ошибки не соответствуют ожиданиям.
    """
    with allure.step("Check user with invalid ID response"):
        assert_invalid_uuid_response(actual=actual, invalid_id=user_id, location=["path", "user_id"])


def assert_create_user_with_empty_password_response(actual: ValidationErrorResponseSchema) -> None:
    """Проверяет ошибку валидации пустого пароля при создании пользователя.

    Args:
        actual: Фактический ответ API с ошибками валидации.

    Raises:
        AssertionError: Если тип, расположение или значение ошибки
            не соответствуют ожидаемым.
    """
    with allure.step("Check create user with empty password response"):
        expected = [
            ValidationErrorExpectation(
                type=ValidationErrorType.STRING_TOO_SHORT,
                input="",
                context={"min_length": 1},
                location=["body", "password"],
            )
        ]
        assert_validation_error_response(actual=actual, expected=expected)
