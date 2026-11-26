from playwright.sync_api import Page

from components.base_component import BaseComponent
from components.courses.create_course_exercise_form_component import (
    CreateCourseExerciseFormComponent,
)
from components.courses.create_course_exercises_toolbar_view_component import (
    CreateCourseExercisesToolbarViewComponent,
)
from components.views.empty_view_component import EmptyViewComponent
from elements.base_element import BaseElement


class CourseExercisesComponent(BaseComponent):
    def __init__(self, page: Page) -> None:
        """Ограничивает редакторы и состояния запросов панелью упражнений курса."""
        panel = page.get_by_test_id("course-exercises-view")
        super().__init__(panel)
        self.toolbar = CreateCourseExercisesToolbarViewComponent(panel)
        self.empty_view = EmptyViewComponent(panel, "create-course-exercises")
        self.save_help = BaseElement(panel, "course-exercises-save-help")
        self.loading = BaseElement(panel, "exercise-loading")
        self.error_alert = BaseElement(panel, "exercise-error-alert")
        self.saved_alert = BaseElement(panel, "exercise-saved-alert")

    def saved(self, exercise_id: str) -> CreateCourseExerciseFormComponent:
        """Возвращает редактор сохранённого упражнения, выбранного по UUID."""
        return CreateCourseExerciseFormComponent(self.root.get_by_test_id(f"exercise-{exercise_id}"))

    def draft(self, index: int) -> CreateCourseExerciseFormComponent:
        """Возвращает редактор несохранённого упражнения по индексу черновика.

        Args:
            index: Число из test ID черновика, начиная с нуля.

        Returns:
            Компонент формы выбранного черновика.
        """
        return CreateCourseExerciseFormComponent(self.root.get_by_test_id(f"create-course-exercise-{index}-draft"))
