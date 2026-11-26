import allure
from playwright.sync_api import Locator, Page

from components.base_component import BaseComponent
from elements.button import Button
from elements.input import Input
from elements.text import Text


class ProfileFormComponent(BaseComponent):
    def __init__(self, root: Page | Locator) -> None:
        """Ограничивает поля и сообщения профиля областью profile-form."""
        super().__init__(root.get_by_test_id("profile-form"))
        self.first_name_input = Input(self.root, "profile-form-first-name-input")
        self.last_name_input = Input(self.root, "profile-form-last-name-input")
        self.middle_name_input = Input(self.root, "profile-form-middle-name-input")
        self.email_input = Input(self.root, "profile-form-email-input")
        self.save_button = Button(self.root, "profile-save-button")
        self.validation_alert = Text(self.root, "profile-validation-alert")
        self.error_alert = Text(self.root, "profile-save-error-alert")
        self.saved_alert = Text(self.root, "profile-saved-alert")
        self.saving_status = Text(self.root, "profile-saving-status")

    @allure.step("Fill profile form")
    def fill(self, first_name: str, last_name: str, middle_name: str, email: str) -> None:
        """Заполняет ФИО и email в форме профиля."""
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.middle_name_input.fill(middle_name)
        self.email_input.fill(email)

    @allure.step("Check profile form values")
    def check_values(self, first_name: str, last_name: str, middle_name: str, email: str) -> None:
        """Сверяет введённые ФИО и email в форме профиля."""
        self.first_name_input.check_have_value(first_name)
        self.last_name_input.check_have_value(last_name)
        self.middle_name_input.check_have_value(middle_name)
        self.email_input.check_have_value(email)

    @allure.step("Check visible profile form")
    def check_visible(self) -> None:
        """Ожидает видимость всех полей профиля и кнопки сохранения."""
        self.first_name_input.check_visible()
        self.last_name_input.check_visible()
        self.middle_name_input.check_visible()
        self.email_input.check_visible()
        self.save_button.check_visible()

    @allure.step("Save profile changes")
    def click_save_button(self) -> None:
        """Отправляет текущие изменения профиля на сохранение."""
        self.save_button.click()
