import re

import allure
from playwright.sync_api import Locator, expect

from components.base_component import BaseComponent
from elements.button import Button
from elements.input import Input
from elements.text import Text


class CreateCourseExerciseFormComponent(BaseComponent):
    root: Locator

    def __init__(self, root: Locator) -> None:
        """Связывает поля и действия одного редактора упражнения.

        Args:
            root: Локатор конкретного сохранённого упражнения или черновика.
                Регулярные выражения для test ID применяются только внутри него.
        """
        super().__init__(root)
        self.title_input = Input(root, re.compile(r"^create-course-exercise-form-title-\d+-input$"))
        self.description_input = Input(root, re.compile(r"^create-course-exercise-form-description-\d+-input$"))
        self.estimated_time_input = Input(root, re.compile(r"^create-course-exercise-form-estimated-time-\d+-input$"))
        self.min_score_input = Input(root, re.compile(r"^create-course-exercise-form-min-score-\d+-input$"))
        self.max_score_input = Input(root, re.compile(r"^create-course-exercise-form-max-score-\d+-input$"))
        self.min_score_error = Text(root, re.compile(r"^create-course-exercise-form-min-score-\d+-error$"))
        self.max_score_error = Text(root, re.compile(r"^create-course-exercise-form-max-score-\d+-error$"))
        self.subtitle = Text(root, re.compile(r"^create-course-exercise-\d+-box-toolbar-subtitle-text$"))
        self.save_button = Button(root, re.compile(r"^create-course-exercise-\d+-save-button$"))
        self.save_status = Text(root, re.compile(r"^create-course-exercise-\d+-save-status$"))
        self.delete_exercise_button = Button(
            root,
            re.compile(r"^create-course-exercise-\d+-box-toolbar-delete-exercise-button$"),
        )

    @allure.step("Delete exercise")
    def click_delete_button(self) -> None:
        """Нажимает удаление выбранного упражнения."""
        self.delete_exercise_button.click()

    @allure.step("Save exercise")
    def click_save_button(self) -> None:
        """Нажимает сохранение выбранного упражнения."""
        self.save_button.click()

    @allure.step("Fill exercise form")
    def fill_create_exercise_form(
        self,
        title: str,
        description: str,
        estimated_time: str | None = None,
        min_score: str | None = None,
        max_score: str | None = None,
    ) -> None:
        """Заполняет поля упражнения и ожидает введённые значения.

        Args:
            title: Название упражнения.
            description: Описание упражнения.
            estimated_time: Длительность. При None текущее поле сохраняется.
            min_score: Строка минимального балла. При None поле сохраняется.
            max_score: Строка максимального балла. При None поле сохраняется.
        """
        self.title_input.fill(title)
        self.title_input.check_have_value(title)
        self.description_input.fill(description)
        self.description_input.check_have_value(description)
        if estimated_time is not None:
            self.estimated_time_input.fill(estimated_time)
            self.estimated_time_input.check_have_value(estimated_time)
        if min_score is not None:
            self.min_score_input.fill(min_score)
            self.min_score_input.check_have_value(min_score)
        if max_score is not None:
            self.max_score_input.fill(max_score)
            self.max_score_input.check_have_value(max_score)

    @allure.step("Check visible exercise form")
    def check_visible(
        self,
        title: str,
        description: str,
        estimated_time: str | None = None,
        min_score: str | None = None,
        max_score: str | None = None,
        position: int | None = None,
    ) -> None:
        """Сверяет видимость редактора, значения полей и заданную позицию.

        Args:
            title: Ожидаемое название упражнения.
            description: Ожидаемое описание упражнения.
            estimated_time: Ожидаемая длительность. None пропускает сверку значения.
            min_score: Ожидаемый минимальный балл. None пропускает сверку значения.
            max_score: Ожидаемый максимальный балл. None пропускает сверку значения.
            position: Номер в подписи упражнения, начиная с единицы.
                None пропускает сверку номера.
        """
        expect(self.root).to_be_visible()
        self.subtitle.check_visible()
        if position is not None:
            self.subtitle.check_have_text(f"#{position} Exercise")
        self.title_input.check_visible()
        self.title_input.check_have_value(title)
        self.description_input.check_visible()
        self.description_input.check_have_value(description)
        self.estimated_time_input.check_visible()
        if estimated_time is not None:
            self.estimated_time_input.check_have_value(estimated_time)
        self.min_score_input.check_visible()
        if min_score is not None:
            self.min_score_input.check_have_value(min_score)
        self.max_score_input.check_visible()
        if max_score is not None:
            self.max_score_input.check_have_value(max_score)
        self.save_button.check_visible()
        self.delete_exercise_button.check_visible()

    @allure.step("Check exercise form is hidden")
    def check_hidden(self) -> None:
        """Ожидает исчезновение выбранного редактора упражнения."""
        expect(self.root).to_be_hidden()
