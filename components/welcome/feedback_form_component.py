import allure
from playwright.sync_api import Page, expect

from components.base_component import BaseComponent


class FeedbackFormComponent(BaseComponent):
    def __init__(self, page: Page) -> None:
        """Связывает тему, текст отзыва и кнопку отправки по доступным ролям."""
        super().__init__(page)
        self.topic_select = page.get_by_role("combobox")
        self.feedback_input = page.get_by_role("textbox", name="Your feedback", exact=True)
        self.send_button = page.get_by_role("button", name="Send Feedback", exact=True)

    @allure.step("Fill feedback form")
    def fill_feedback(self, feedback: str) -> None:
        """Вводит текст отзыва в поле обратной связи."""
        self.feedback_input.fill(feedback)

    @allure.step("Select feedback topic")
    def select_topic(self, title: str) -> None:
        """Открывает список тем и выбирает вариант с точным названием."""
        self.topic_select.click()
        self.root.get_by_role("option", name=title, exact=True).click()

    @allure.step("Check visible feedback form")
    def check_visible(self) -> None:
        """Ожидает видимость выбора темы, текста отзыва и кнопки отправки."""
        expect(self.topic_select).to_be_visible()
        expect(self.feedback_input).to_be_visible()
        expect(self.send_button).to_be_visible()

    @allure.step("Check feedback submission is unavailable")
    def check_submission_unavailable(self) -> None:
        """Ожидает недоступную кнопку отправки обратной связи."""
        expect(self.send_button).to_be_disabled()
