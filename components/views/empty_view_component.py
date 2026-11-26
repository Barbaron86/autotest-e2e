import allure
from playwright.sync_api import Locator, Page

from components.base_component import BaseComponent
from elements.icon import Icon
from elements.text import Text


class EmptyViewComponent(BaseComponent):
    def __init__(self, root: Page | Locator, identifier: str) -> None:
        """Связывает элементы сообщения о пустом состоянии по префиксу test ID.

        Args:
            root: Область поиска сообщения.
            identifier: Префикс test ID иконки, заголовка и описания.
        """
        super().__init__(root)
        self.icon = Icon(root, f"{identifier}-empty-view-icon")
        self.title = Text(root, f"{identifier}-empty-view-title-text")
        self.description = Text(root, f"{identifier}-empty-view-description-text")

    @allure.step("Check visible empty view")
    def check_visible(self, title: str, description: str) -> None:
        """Ожидает иконку и заданные тексты заголовка и описания пустого состояния."""
        self.icon.check_visible()
        self.title.check_visible()
        self.title.check_have_text(title)
        self.description.check_visible()
        self.description.check_have_text(description)
