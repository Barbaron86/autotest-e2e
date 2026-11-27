from http import HTTPStatus
from http.cookies import CookieError, SimpleCookie

import allure
from httpx import Response

from clients.error_schema import InternalErrorResponseSchema, ValidationErrorResponseSchema
from tools.assertions.base import assert_equal, assert_is_true, assert_status_code
from tools.assertions.errors import (
    ValidationErrorExpectation,
    assert_internal_error_response,
    assert_validation_error_response,
)
from tools.error_messages import ApiErrorMessage
from tools.error_types import ValidationErrorType
from tools.routes import APIRoutes


def _assert_cookie_session_response(response: Response) -> None:
    """Проверяет HTTP 204, пустое тело и обе непустые cookies сессии."""
    assert_status_code(response.status_code, HTTPStatus.NO_CONTENT)
    assert_equal(len(response.content), 0, "authentication response body size")
    cookie_names = {cookie.name for cookie in response.cookies.jar if cookie.value}
    assert_is_true({"access_token", "refresh_token"} <= cookie_names, "session cookies present")


def assert_login_response(response: Response) -> None:
    """Проверяет успешный cookie-login без записи значений cookies в отчёт."""
    with allure.step("Check login response"):
        _assert_cookie_session_response(response)


def assert_refresh_response(response: Response) -> None:
    """Проверяет HTTP 204, пустое тело и наличие двух cookies после Refresh."""
    with allure.step("Check refresh response"):
        _assert_cookie_session_response(response)


def assert_logout_response(response: Response) -> None:
    """Проверяет HTTP 204 и удаление обеих cookies с исходных путей."""
    with allure.step("Check logout response"):
        assert_status_code(response.status_code, HTTPStatus.NO_CONTENT)
        assert_equal(len(response.content), 0, "authentication response body size")
        expected_cookies = {("access_token", "/api/v1"), ("refresh_token", APIRoutes.AUTHENTICATION)}
        assert_is_true(
            expected_cookies <= _deleted_cookie_targets(response), "session cookies removed at original paths"
        )


def _deleted_cookie_targets(response: Response) -> set[tuple[str, str]]:
    """Возвращает имена и пути удаляемых cookies, скрывая значения и ошибки разбора."""
    deleted: set[tuple[str, str]] = set()
    try:
        for header in response.headers.get_list("set-cookie"):
            cookies = SimpleCookie()
            cookies.load(header)
            deleted.update((name, cookie["path"]) for name, cookie in cookies.items() if cookie["max-age"] == "0")
    except CookieError:
        return set()
    return deleted


def assert_invalid_refresh_token_response(actual: InternalErrorResponseSchema) -> None:
    """Проверяет причину отказа в обновлении невалидного refresh-токена.

    Args:
        actual: Фактический ответ API с сообщением об ошибке.

    Raises:
        AssertionError: Если сообщение не соответствует невалидному refresh-токену.
    """
    with allure.step("Check invalid refresh token response"):
        expected = InternalErrorResponseSchema(detail=ApiErrorMessage.INVALID_OR_EXPIRED_REFRESH_TOKEN)
        assert_internal_error_response(actual=actual, expected=expected)


def assert_invalid_credentials_response(actual: InternalErrorResponseSchema) -> None:
    """Проверяет причину отказа во входе с неверными учетными данными.

    Args:
        actual: Фактический ответ API с сообщением об ошибке.

    Raises:
        AssertionError: Если сообщение не соответствует неверным учетным данным.
    """
    with allure.step("Check invalid credentials response"):
        expected = InternalErrorResponseSchema(detail=ApiErrorMessage.INVALID_CREDENTIALS)
        assert_internal_error_response(actual=actual, expected=expected)


def assert_login_with_invalid_email_type_response(actual: ValidationErrorResponseSchema, email: object) -> None:
    """Проверяет ошибку валидации некорректного типа email.

    Args:
        actual: Фактический ответ API с ошибками валидации.
        email: Некорректное значение email из запроса.

    Raises:
        AssertionError: Если ошибка валидации не соответствует ожиданиям.
    """
    with allure.step("Check login with invalid email type response"):
        expected = [
            ValidationErrorExpectation(type=ValidationErrorType.STRING_TYPE, input=email, location=["body", "email"])
        ]
        assert_validation_error_response(actual=actual, expected=expected)
