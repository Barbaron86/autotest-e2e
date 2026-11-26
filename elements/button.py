from playwright.sync_api import expect

from elements.base_element import BaseElement


class Button(BaseElement):
    def check_enabled(self) -> None:
        """Ожидает доступную для нажатия кнопку."""
        with self.step("Check enabled"):
            expect(self.get_locator()).to_be_enabled()

    def check_disabled(self) -> None:
        """Ожидает недоступную для нажатия кнопку."""
        with self.step("Check disabled"):
            expect(self.get_locator()).to_be_disabled()
