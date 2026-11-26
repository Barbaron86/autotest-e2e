from collections.abc import Iterator
from contextlib import contextmanager
from re import Pattern

from playwright.sync_api import Locator, Page, expect

from tools.ui_steps import ui_step


class BaseElement:
    def __init__(self, root: Page | Locator, test_id: str | Pattern[str]) -> None:
        """Сохраняет область поиска и test ID элемента для последующих действий.

        Args:
            root: Страница или локатор, ограничивающий поиск элемента.
            test_id: Точное значение либо регулярное выражение data-testid.
        """
        self.root = root
        self.test_id = test_id

    def get_locator(self) -> Locator:
        """Возвращает локатор элемента по test ID внутри заданной области."""
        return self.root.get_by_test_id(self.test_id)

    @contextmanager
    def step(self, action: str) -> Iterator[None]:
        """Создаёт шаг Allure и безопасное сообщение Loguru для действия.

        Args:
            action: Название действия без значений пользовательского ввода.

        Yields:
            Управление коду действия внутри шага.
        """
        with ui_step(f"{action} [{self.test_id}]"):
            yield

    def click(self) -> None:
        """Нажимает элемент после проверок доступности Playwright."""
        with self.step("Click"):
            self.get_locator().click()

    def check_visible(self) -> None:
        """Ожидает видимость элемента."""
        with self.step("Check visibility"):
            expect(self.get_locator()).to_be_visible()

    def check_hidden(self) -> None:
        """Ожидает, что элемент скрыт или отсутствует в DOM."""
        with self.step("Check hidden"):
            expect(self.get_locator()).to_be_hidden()

    def check_have_text(self, text: str | Pattern[str]) -> None:
        """Ожидает текст элемента по строке или регулярному выражению."""
        with self.step("Check text"):
            expect(self.get_locator()).to_have_text(text)
