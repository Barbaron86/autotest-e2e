from playwright.sync_api import Page

from components.welcome.feedback_form_component import FeedbackFormComponent
from components.welcome.subscription_form_component import SubscriptionFormComponent
from elements.button import Button
from elements.text import Text
from pages.base_page import BasePage


class WelcomePage(BasePage):
    def __init__(self, page: Page) -> None:
        """Связывает заголовок, внешнюю ссылку и формы приветственной страницы."""
        super().__init__(page)
        self.title = Text(page, "welcome-toolbar-title-text")
        self.github_button = Button(page, "welcome-toolbar-github-button")
        self.subscription_form = SubscriptionFormComponent(page)
        self.feedback_form = FeedbackFormComponent(page)
