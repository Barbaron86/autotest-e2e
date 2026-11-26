import allure
from playwright.sync_api import Locator, Page

from components.base_component import BaseComponent
from elements.input import Input


class RegistrationFormComponent(BaseComponent):
    def __init__(self, root: Page | Locator) -> None:
        """Связывает поля email, ФИО и пароля с областью формы регистрации."""
        super().__init__(root)
        self.email_input = Input(root, "registration-form-email-input")
        self.first_name_input = Input(root, "registration-form-first-name-input")
        self.last_name_input = Input(root, "registration-form-last-name-input")
        self.middle_name_input = Input(root, "registration-form-middle-name-input")
        self.password_input = Input(root, "registration-form-password-input", sensitive=True)

    def fill(self, email: str, first_name: str, last_name: str, middle_name: str, password: str) -> None:
        """Заполняет все поля регистрации и ожидает введённые значения."""
        self.email_input.fill(email)
        self.email_input.check_have_value(email)
        self.first_name_input.fill(first_name)
        self.first_name_input.check_have_value(first_name)
        self.last_name_input.fill(last_name)
        self.last_name_input.check_have_value(last_name)
        self.middle_name_input.fill(middle_name)
        self.middle_name_input.check_have_value(middle_name)
        self.password_input.fill(password)
        self.password_input.check_have_value(password)

    @allure.step("Check visible registration form")
    def check_visible(self) -> None:
        """Ожидает видимость всех обязательных полей регистрации."""
        self.email_input.check_visible()
        self.first_name_input.check_visible()
        self.last_name_input.check_visible()
        self.middle_name_input.check_visible()
        self.password_input.check_visible()

    def check_values(self, email: str, first_name: str, last_name: str, middle_name: str, password: str) -> None:
        """Сверяет текущие значения email, ФИО и пароля без отправки формы."""
        self.email_input.check_have_value(email)
        self.first_name_input.check_have_value(first_name)
        self.last_name_input.check_have_value(last_name)
        self.middle_name_input.check_have_value(middle_name)
        self.password_input.check_have_value(password)
