import allure
from playwright.sync_api import Locator, Page

from components.base_component import BaseComponent
from elements.button import Button
from elements.text import Text


class CreateCourseExercisesToolbarViewComponent(BaseComponent):
    def __init__(self, root: Page | Locator) -> None:
        """Связывает заголовок секции упражнений и кнопку добавления."""
        super().__init__(root)
        self.title = Text(root, "create-course-exercises-box-toolbar-title-text")
        self.create_exercise_button = Button(root, "create-course-exercises-box-toolbar-create-exercise-button")

    @allure.step("Check visible exercises toolbar")
    def check_visible(self) -> None:
        """Ожидает заголовок секции упражнений и кнопку добавления."""
        self.title.check_visible()
        self.title.check_have_text("Exercises")
        self.create_exercise_button.check_visible()

    @allure.step("Add exercise draft")
    def click_create_exercise_button(self) -> None:
        """Добавляет в редактор новый несохранённый черновик упражнения."""
        self.create_exercise_button.click()
