import allure
from playwright.sync_api import Locator, Page

from components.base_component import BaseComponent
from elements.link import Link
from elements.text import Text
from tools.routes import AppRoute


class NavbarComponent(BaseComponent):
    def __init__(self, root: Page | Locator) -> None:
        """Связывает название приложения, приветствие и ссылку профиля."""
        super().__init__(root)
        self.app_title = Text(root, "navigation-navbar-app-title-text")
        self.welcome_title = Text(root, "navigation-navbar-welcome-title-text")
        self.profile_button = Link(root, "navigation-navbar-profile-button")

    @allure.step("Check visible navbar")
    def check_visible(self, first_name: str, last_name: str) -> None:
        """Сверяет название приложения, приветствие пользователя и ссылку профиля."""
        self.app_title.check_visible()
        self.app_title.check_have_text("QA Course App")
        self.welcome_title.check_visible()
        self.welcome_title.check_have_text(f"Welcome, {first_name} {last_name}!")
        self.profile_button.check_visible()

    @allure.step("Open profile from navbar")
    def click_profile(self) -> None:
        """Переходит в профиль через верхнюю панель и ожидает его маршрут."""
        self.profile_button.click()
        self.check_current_url(AppRoute.PROFILE)
