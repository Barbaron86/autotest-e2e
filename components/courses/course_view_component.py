import allure
from playwright.sync_api import Locator, Page, expect

from components.base_component import BaseComponent
from components.courses.course_view_menu_component import CourseViewMenuComponent
from elements.image import Image
from elements.text import Text


class CourseViewComponent(BaseComponent):
    root: Locator

    def __init__(self, page: Page, course_id: str) -> None:
        """Ограничивает поля карточкой курса с указанным UUID."""
        card = page.get_by_test_id(f"course-{course_id}")
        super().__init__(card)
        self.menu = CourseViewMenuComponent(page, card)
        self.title = Text(card, "course-widget-title-text")
        self.image = Image(card, "course-preview-image")
        self.max_score_text = Text(card, "course-max-score-info-row-view-text")
        self.min_score_text = Text(card, "course-min-score-info-row-view-text")
        self.estimated_time_text = Text(card, "course-estimated-time-info-row-view-text")
        self.preview_error = Text(card, "course-preview-error-alert")
        self.preview_loading = Text(card, "course-preview-loading")

    @allure.step("Check visible course card")
    def check_visible(self, title: str, max_score: str, min_score: str, estimated_time: str) -> None:
        """Сверяет загруженную обложку и значения полей выбранной карточки.

        Args:
            title: Ожидаемое название курса.
            max_score: Текст максимального балла без подписи поля.
            min_score: Текст минимального балла без подписи поля.
            estimated_time: Текст длительности без подписи поля.
        """
        expect(self.root).to_be_visible()
        self.image.check_loaded()
        self.title.check_visible()
        self.title.check_have_text(title)
        self.max_score_text.check_visible()
        self.max_score_text.check_have_text(f"Max score: {max_score}")
        self.min_score_text.check_visible()
        self.min_score_text.check_have_text(f"Min score: {min_score}")
        self.estimated_time_text.check_visible()
        self.estimated_time_text.check_have_text(f"Estimated time: {estimated_time}")

    @allure.step("Check course card is hidden")
    def check_hidden(self) -> None:
        """Ожидает исчезновение карточки выбранного курса."""
        expect(self.root).to_be_hidden()
