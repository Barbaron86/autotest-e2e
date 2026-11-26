from collections.abc import Callable
from re import Pattern

import allure
from playwright.sync_api import Page, Response, expect

from tools.browser_responses import matches_api_response
from tools.ui_steps import ui_logger, ui_step


class BasePage:
    def __init__(self, page: Page) -> None:
        """Связывает объект страницы с открытой вкладкой Playwright."""
        self.page = page

    def visit(self, url: str) -> None:
        """Открывает URL относительно настроенного base_url браузера."""
        with ui_step(f"Open {type(self).__name__}"):
            self.page.goto(url)

    @allure.step("Reload current page")
    def reload(self) -> None:
        """Перезагружает текущую вкладку и добавляет шаг в отчёт."""
        ui_logger.debug(f"Reload {type(self).__name__}")
        self.page.reload()

    def _wait_for_api_response(self, method: str, path: str, action: Callable[[], None]) -> Response:
        """Выполняет действие после установки ожидания конкретного API-ответа.

        Args:
            method: HTTP-метод ожидаемого запроса.
            path: Точный путь URL без хоста и query-параметров.
            action: Действие, которое инициирует ожидаемый запрос.

        Returns:
            Ответ браузера, совпавший по методу и пути. Статус не проверяется.

        Raises:
            playwright.sync_api.TimeoutError: Если ответ не получен вовремя.
        """
        with self.page.expect_response(lambda response: matches_api_response(response, method, path)) as pending:
            action()
        return pending.value

    def check_current_url(self, expected_url: str | Pattern[str]) -> None:
        """Ожидает совпадения URL вкладки со строкой или регулярным выражением."""
        with ui_step(f"Check URL for {type(self).__name__}"):
            expect(self.page).to_have_url(expected_url)
