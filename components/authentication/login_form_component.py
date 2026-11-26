import allure
from playwright.sync_api import Locator, Page

from components.base_component import BaseComponent
from elements.input import Input


class LoginFormComponent(BaseComponent):
    def __init__(self, root: Page | Locator) -> None:
        """Связывает поля email и пароля с корневой областью формы входа."""
        super().__init__(root)
        self.email_input = Input(root, "login-form-email-input")
        self.password_input = Input(root, "login-form-password-input", sensitive=True)

    def fill(self, email: str, password: str) -> None:
        """Заполняет email и пароль и ожидает введённые значения полей."""
        self.email_input.fill(email)
        self.email_input.check_have_value(email)
        self.password_input.fill(password)
        self.password_input.check_have_value(password)

    @allure.step("Check visible login form")
    def check_visible(self) -> None:
        """Ожидает видимость полей email и пароля."""
        self.email_input.check_visible()
        self.password_input.check_visible()

    def check_values(self, email: str, password: str) -> None:
        """Сверяет текущие значения email и пароля без отправки формы."""
        self.email_input.check_have_value(email)
        self.password_input.check_have_value(password)
