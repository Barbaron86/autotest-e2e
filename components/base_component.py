from re import Pattern

from playwright.sync_api import Locator, Page, expect


class BaseComponent:
    def __init__(self, root: Page | Locator) -> None:
        """Ограничивает поиск элементов переданной страницей или локатором."""
        self.root = root

    def check_current_url(self, expected_url: str | Pattern[str]) -> None:
        """Ожидает заданный URL вкладки, которой принадлежит компонент."""
        page = self.root if isinstance(self.root, Page) else self.root.page
        expect(page).to_have_url(expected_url)
