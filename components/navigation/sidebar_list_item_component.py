import re
from re import Pattern

import allure
from playwright.sync_api import Locator, Page, expect

from components.base_component import BaseComponent
from elements.button import Button
from elements.icon import Icon
from elements.text import Text


class SidebarListItemComponent(BaseComponent):
    def __init__(self, root: Page | Locator, identifier: str) -> None:
        """Связывает иконку, подпись и кнопку пункта боковой навигации.

        Args:
            root: Область поиска элементов боковой навигации.
            identifier: Префикс test ID пункта, например courses или logout.
        """
        super().__init__(root)
        self.icon = Icon(root, f"{identifier}-drawer-list-item-icon")
        self.title = Text(root, f"{identifier}-drawer-list-item-title-text")
        self.button = Button(root, f"{identifier}-drawer-list-item-button")

    @allure.step("Check visible sidebar item")
    def check_visible(self, title: str) -> None:
        """Ожидает иконку, кнопку и заданную подпись пункта навигации."""
        self.icon.check_visible()
        self.title.check_visible()
        self.title.check_have_text(title)
        self.button.check_visible()

    @allure.step("Click sidebar item")
    def click(self) -> None:
        """Нажимает кнопку выбранного пункта навигации."""
        self.button.click()

    @allure.step("Navigate from sidebar item")
    def navigate(self, expected_url: str | Pattern[str]) -> None:
        """Нажимает пункт навигации и ожидает заданный URL."""
        self.button.click()
        self.check_current_url(expected_url)

    @allure.step("Check selected sidebar item")
    def check_selected(self) -> None:
        """Проверяет класс MUI, отмечающий текущий пункт навигации."""
        expect(self.button.get_locator()).to_have_class(re.compile(r"\bMui-selected\b"))
