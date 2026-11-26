from json import dumps
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Page
from pytest import FixtureRequest

from config import settings
from fixtures.users import AuthenticatedAccount
from tools.allure.artifacts import BROWSER_ARTIFACTS_PATH

AUTH_STORAGE_KEY = "qa-course-app-session"
AUTH_SEEDED_KEY = "autotest-e2e-session-seeded"


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
    """Подготавливает браузерную сессию без отправки формы входа.

    Скрипт записывает токены один раз при открытии верхнего документа
    на origin приложения и сохраняет уже существующую сессию. После
    инициализации обновление токенов и выход выполняет само приложение.

    Args:
        page: Страница в отдельном контексте теста.
        authenticated_account: Аккаунт с токенами, полученными через API.
        browser_context_args: Параметры контекста с базовым URL интерфейса.

    Returns:
        Та же страница со скриптом инициализации сессии.
    """
    origin = dumps(str(browser_context_args["base_url"]))
    token_json = dumps(authenticated_account.token.model_dump_json(by_alias=True))
    # Initialise only the first top-level document on the UI origin. Logout and refresh own the state afterwards.
    page.add_init_script(
        f"""
        (() => {{
            if (window !== window.top || location.origin !== new URL({origin}).origin) return;
            if (sessionStorage.getItem({dumps(AUTH_SEEDED_KEY)}) !== null) return;
            if (sessionStorage.getItem({dumps(AUTH_STORAGE_KEY)}) === null) {{
                sessionStorage.setItem({dumps(AUTH_STORAGE_KEY)}, {token_json});
            }}
            sessionStorage.setItem({dumps(AUTH_SEEDED_KEY)}, "1");
        }})();
        """
    )
    return page
