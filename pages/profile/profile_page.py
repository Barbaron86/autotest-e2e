from playwright.sync_api import Page

from components.navigation.navbar_component import NavbarComponent
from components.navigation.sidebar_component import SidebarComponent
from components.profile.profile_form_component import ProfileFormComponent
from elements.button import Button
from elements.text import Text
from pages.base_page import BasePage


class ProfilePage(BasePage):
    def __init__(self, page: Page) -> None:
        """Связывает форму профиля и состояния загрузки с вкладкой."""
        super().__init__(page)
        self.navbar = NavbarComponent(page)
        self.sidebar = SidebarComponent(page)
        self.title = Text(page, "profile-title")
        self.profile_form = ProfileFormComponent(page)
        self.load_error_alert = Text(page, "profile-load-error-alert")
        self.retry_button = Button(page, "profile-retry-button")
        self.loading_status = Text(page, "profile-loading-status")
