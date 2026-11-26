import allure
from playwright.sync_api import Page, expect

from components.base_component import BaseComponent


class SubscriptionFormComponent(BaseComponent):
    def __init__(self, page: Page) -> None:
        """Связывает email, согласие на рассылку и кнопку подписки по ролям."""
        super().__init__(page)
        self.email_input = page.get_by_role("textbox", name="Email", exact=True)
        self.agreement_checkbox = page.get_by_role("checkbox", name="I agree to receive updates", exact=True)
        self.subscribe_button = page.get_by_role("button", name="Subscribe", exact=True)

    @allure.step("Fill subscription email")
    def fill_email(self, email: str) -> None:
        """Вводит email в поле подписки на рассылку."""
        self.email_input.fill(email)

    @allure.step("Check visible subscription form")
    def check_visible(self) -> None:
        """Ожидает видимость email, согласия и кнопки подписки."""
        expect(self.email_input).to_be_visible()
        expect(self.agreement_checkbox).to_be_visible()
        expect(self.subscribe_button).to_be_visible()

    @allure.step("Check subscription submission is unavailable")
    def check_submission_unavailable(self) -> None:
        """Ожидает недоступную кнопку подписки на рассылку."""
        expect(self.subscribe_button).to_be_disabled()
