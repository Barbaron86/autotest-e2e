from re import Pattern

import allure
from playwright.sync_api import Page

from elements.button import Button
from elements.text import Text
from pages.base_page import BasePage
from tools.routes import AppRoute


class NotFoundPage(BasePage):
    def __init__(self, page: Page) -> None:
        """Связывает сообщение о неизвестном маршруте и кнопку перехода со вкладкой."""
        super().__init__(page)
        self.title = Text(page, "page-not-found-title-text")
        self.dashboard_button = Button(page, "go-to-dashboard-page-button")

    @allure.step("Navigate from page not found")
    def click_dashboard_button(self, expected_url: str | Pattern[str] = AppRoute.DASHBOARD) -> None:
        """Нажимает кнопку перехода на сводную страницу и ожидает указанный URL."""
        self.dashboard_button.click()
        self.check_current_url(expected_url)
