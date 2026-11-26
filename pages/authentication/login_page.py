import allure
from playwright.sync_api import Page

from components.authentication.login_form_component import LoginFormComponent
from elements.button import Button
from elements.link import Link
from elements.text import Text
from pages.base_page import BasePage
from tools.routes import AppRoute


class LoginPage(BasePage):
    def __init__(self, page: Page) -> None:
        """Связывает форму входа, навигацию и сообщения авторизации с вкладкой."""
        super().__init__(page)
        self.login_form = LoginFormComponent(page)
        self.login_button = Button(page, "login-page-login-button")
        self.registration_link = Link(page, "login-page-registration-link")
        self.wrong_email_or_password_alert = Text(page, "login-page-wrong-email-or-password-alert")
        self.error_alert = Text(page, "login-page-error-alert")
        self.session_expired_alert = Text(page, "authentication-session-expired-alert")
        self.pending_status = Text(page, "login-page-pending-status")

    @allure.step("Submit login form")
    def click_login_button(self) -> None:
        """Отправляет заполненную форму входа."""
        self.login_button.click()

    @allure.step("Open registration page")
    def click_registration_link(self) -> None:
        """Переходит по ссылке регистрации и ожидает её маршрут."""
        self.registration_link.click()
        self.check_current_url(AppRoute.REGISTRATION)

    @allure.step("Check visible wrong email or password alert")
    def check_visible_wrong_email_or_password_alert(self) -> None:
        """Ожидает сообщение о неверном email или пароле с точным текстом."""
        self.wrong_email_or_password_alert.check_visible()
        self.wrong_email_or_password_alert.check_have_text("Wrong email or password")
