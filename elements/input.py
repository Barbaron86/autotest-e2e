from collections.abc import Iterator
from contextlib import contextmanager
from re import Pattern

from playwright.sync_api import Error, Locator, Page, expect

from elements.base_element import BaseElement


class Input(BaseElement):
    control_selector = "input"

    def __init__(self, root: Page | Locator, test_id: str | Pattern[str], *, sensitive: bool = False) -> None:
        """Связывает поле ввода с корневой областью и режимом диагностики.

        Args:
            root: Страница или локатор, ограничивающий поиск поля.
            test_id: Test ID контейнера поля либо регулярное выражение.
            sensitive: Заменяет ошибки ввода и сверки безопасным сообщением,
                чтобы скрыть значения чувствительного поля.
        """
        super().__init__(root, test_id)
        self.sensitive = sensitive

    def get_locator(self) -> Locator:
        """Возвращает вложенный input или textarea внутри контейнера по test ID."""
        return super().get_locator().locator(self.control_selector)

    def fill(self, value: str) -> None:
        """Заменяет значение поля с учётом режима безопасной диагностики."""
        with self._input_step("Fill input"):
            self.get_locator().fill(value)

    def check_have_value(self, value: str) -> None:
        """Ожидает значение поля с учётом режима безопасной диагностики."""
        with self._input_step("Check input value"):
            expect(self.get_locator()).to_have_value(value)

    @contextmanager
    def _input_step(self, action: str) -> Iterator[None]:
        """Выполняет действие поля внутри отчётного шага.

        Args:
            action: Название действия без содержимого поля.

        Yields:
            Управление действию заполнения или сверки значения.

        Raises:
            AssertionError: Ошибка Playwright или сверки для sensitive-поля,
                заменённая сообщением без значения поля.
        """
        with self.step(action):
            try:
                yield
            except (Error, AssertionError):
                if self.sensitive:
                    raise AssertionError(f"{action} failed for sensitive field {self.test_id!r}") from None
                raise
