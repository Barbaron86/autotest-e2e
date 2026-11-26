import allure
from playwright.sync_api import Page

from components.authentication.registration_form_component import RegistrationFormComponent
from elements.button import Button
from elements.link import Link
from elements.text import Text
from pages.base_page import BasePage
from tools.routes import AppRoute


class RegistrationPage(BasePage):
    def __init__(self, page: Page) -> None:
        """Связывает поля регистрации, навигацию и сообщения об ошибках с вкладкой."""
        super().__init__(page)
        self.registration_form = RegistrationFormComponent(page)
        self.registration_button = Button(page, "registration-page-registration-button")
        self.login_link = Link(page, "registration-page-login-link")
        self.user_already_exists_alert = Text(page, "registration-page-user-already-exists-alert")
        self.error_alert = Text(page, "registration-page-error-alert")
        self.pending_status = Text(page, "registration-page-pending-status")

    @allure.step("Submit registration form")
    def click_registration_button(self) -> None:
        """Отправляет заполненную форму регистрации."""
        self.registration_button.click()

    @allure.step("Open login page")
    def click_login_link(self) -> None:
        """Переходит по ссылке входа и ожидает её маршрут."""
        self.login_link.click()
        self.check_current_url(AppRoute.LOGIN)

    @allure.step("Check visible user already exists alert")
    def check_visible_user_already_exists_alert(self) -> None:
        """Ожидает сообщение о существующем пользователе с точным текстом."""
        self.user_already_exists_alert.check_visible()
        self.user_already_exists_alert.check_have_text("User already exists")
