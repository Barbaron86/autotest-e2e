import allure
from playwright.sync_api import Locator, Page

from components.base_component import BaseComponent
from elements.text import Text


class DashboardToolbarViewComponent(BaseComponent):
    def __init__(self, root: Page | Locator) -> None:
        """Связывает заголовок сводной страницы с корневой областью."""
        super().__init__(root)
        self.title = Text(root, "dashboard-toolbar-title-text")

    @allure.step("Check visible dashboard toolbar")
    def check_visible(self) -> None:
        """Ожидает видимый заголовок сводной страницы с точным текстом."""
        self.title.check_visible()
        self.title.check_have_text("Dashboard")
