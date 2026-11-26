import allure
from playwright.sync_api import Locator, Page

from components.base_component import BaseComponent
from elements.input import Input
from elements.text import Text
from elements.textarea import Textarea


class CreateCourseFormComponent(BaseComponent):
    def __init__(self, root: Page | Locator) -> None:
        """Связывает поля курса и сообщения проверки баллов с областью формы."""
        super().__init__(root)
        self.title_input = Input(root, "create-course-form-title-input")
        self.description_textarea = Textarea(root, "create-course-form-description-input")
        self.estimated_time_input = Input(root, "create-course-form-estimated-time-input")
        self.min_score_input = Input(root, "create-course-form-min-score-input")
        self.max_score_input = Input(root, "create-course-form-max-score-input")
        self.min_score_error = Text(root, "create-course-form-min-score-error")
        self.max_score_error = Text(root, "create-course-form-max-score-error")

    @allure.step("Check visible course form")
    def check_visible(
        self,
        title: str,
        estimated_time: str,
        description: str,
        max_score: str,
        min_score: str,
    ) -> None:
        """Сверяет видимость и ожидаемые значения всех полей курса."""
        self.title_input.check_visible()
        self.title_input.check_have_value(title)
        self.estimated_time_input.check_visible()
        self.estimated_time_input.check_have_value(estimated_time)
        self.description_textarea.check_visible()
        self.description_textarea.check_have_value(description)
        self.max_score_input.check_visible()
        self.max_score_input.check_have_value(max_score)
        self.min_score_input.check_visible()
        self.min_score_input.check_have_value(min_score)

    @allure.step("Fill course form")
    def fill(
        self,
        title: str,
        estimated_time: str,
        description: str,
        max_score: str,
        min_score: str,
    ) -> None:
        """Заполняет все поля курса и ожидает введённые значения.

        Args:
            title: Название курса.
            estimated_time: Длительность курса в отображаемом формате.
            description: Описание курса.
            max_score: Строка для поля максимального балла.
            min_score: Строка для поля минимального балла.
        """
        self.title_input.fill(title)
        self.title_input.check_have_value(title)
        self.estimated_time_input.fill(estimated_time)
        self.estimated_time_input.check_have_value(estimated_time)
        self.description_textarea.fill(description)
        self.description_textarea.check_have_value(description)
        self.max_score_input.fill(max_score)
        self.max_score_input.check_have_value(max_score)
        self.min_score_input.fill(min_score)
        self.min_score_input.check_have_value(min_score)
