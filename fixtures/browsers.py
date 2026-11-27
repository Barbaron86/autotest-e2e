from http import HTTPStatus
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import allure
import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page
from pytest import FixtureRequest

from config import settings
from fixtures.users import AuthenticatedAccount
from tools.allure.artifacts import BROWSER_ARTIFACTS_PATH
from tools.assertions.base import assert_equal, assert_status_code
from tools.routes import APIRoutes


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict[str, Any]) -> dict[str, Any]:
    """Добавляет адрес интерфейса, сохраняя параметры pytest-playwright.

    Args:
        browser_context_args: Исходные параметры, включая CLI-адрес,
            эмуляцию устройства и каталог видео.

    Returns:
        Параметры браузерного контекста с адресом интерфейса.
    """
    return {"base_url": str(settings.ui_base_url), **browser_context_args}


@pytest.fixture
def output_path(output_path: str, request: FixtureRequest) -> str:
    """Запоминает каталог Playwright до завершения остальных фикстур теста.

    Allure использует этот путь и при ошибке дальнейшей подготовки теста.

    Args:
        output_path: Каталог текущего теста из pytest-playwright.
        request: Запрос текущей фикстуры для доступа к тесту.

    Returns:
        Исходный каталог Playwright.
    """
    request.node.stash[BROWSER_ARTIFACTS_PATH] = Path(output_path)
    return output_path


@pytest.fixture
def authenticated_page(
    page: Page, authenticated_account: AuthenticatedAccount, browser_context_args: dict[str, Any]
) -> Page:
    """Входит через API в отдельную браузерную сессию тестового аккаунта.

    APIRequestContext браузера автоматически сохраняет cookies ответа.
    HTTPX-сессия того же пользователя продолжает работать независимо.

    Args:
        page: Страница в отдельном контексте теста.
        authenticated_account: Пользователь и отдельная HTTPX-сессия для API-проверок.
        browser_context_args: Параметры контекста с базовым URL интерфейса.

    Returns:
        Та же страница в контексте с авторизованной cookie-сессией.

    Raises:
        RuntimeError: Браузерный API-клиент не смог выполнить вход.
        AssertionError: Ответ входа отличается от HTTP 204 с пустым телом.
    """
    ui_url = urlsplit(str(browser_context_args["base_url"]))
    origin = f"{ui_url.scheme}://{ui_url.netloc}"
    credentials = authenticated_account.user.authentication_user
    with allure.step("Authenticate browser user"):
        try:
            response = page.context.request.post(
                f"{origin}{APIRoutes.AUTHENTICATION}/login",
                data={"email": str(credentials.email), "password": credentials.password},
                headers={"Origin": origin},
                timeout=settings.api_timeout * 1000,
                max_redirects=0,
            )
            try:
                status = response.status
                body_size = len(response.body())
            finally:
                response.dispose()
        except PlaywrightError:
            raise RuntimeError("Не удалось выполнить браузерный API-вход тестового пользователя.") from None
        assert_status_code(status, HTTPStatus.NO_CONTENT)
        assert_equal(body_size, 0, "browser login response body size")
    return page
