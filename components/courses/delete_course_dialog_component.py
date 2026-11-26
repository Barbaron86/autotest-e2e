import allure
from playwright.sync_api import Locator, Page, expect

from components.base_component import BaseComponent
from elements.base_element import BaseElement
from elements.button import Button


class DeleteCourseDialogComponent(BaseComponent):
    root: Locator

    def __init__(self, page: Page) -> None:
        """Ограничивает кнопки и состояния диалогом с заголовком удаления курса."""
        dialog = page.get_by_role("dialog").filter(
            has=page.get_by_test_id("modal-title-text").filter(has_text="Delete course")
        )
        super().__init__(dialog)
        self.title = BaseElement(dialog, "modal-title-text")
        self.confirm_button = Button(dialog, "modal-confirm-button")
        self.cancel_button = Button(dialog, "modal-cancel-button")
        self.close_button = Button(dialog, "modal-close-button")
        self.error_alert = BaseElement(dialog, "course-delete-error-alert")
        self.loading = BaseElement(dialog, "course-delete-loading")

    @allure.step("Check visible delete course dialog")
    def check_visible(self) -> None:
        """Ожидает видимость диалога подтверждения удаления курса."""
        expect(self.root).to_be_visible()

    @allure.step("Check delete course dialog is hidden")
    def check_hidden(self) -> None:
        """Ожидает закрытие диалога подтверждения удаления курса."""
        expect(self.root).to_be_hidden()
