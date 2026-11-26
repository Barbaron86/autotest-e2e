from collections.abc import Callable

import allure
from playwright.sync_api import Page, Response

from components.courses.course_exercises_component import CourseExercisesComponent
from components.courses.create_course_form_component import CreateCourseFormComponent
from components.courses.create_course_toolbar_view_component import (
    CreateCourseToolbarViewComponent,
)
from components.navigation.navbar_component import NavbarComponent
from components.navigation.sidebar_component import SidebarComponent
from components.views.image_upload_widget_component import ImageUploadWidgetComponent
from elements.base_element import BaseElement
from elements.button import Button
from pages.base_page import BasePage
from tools.browser_responses import matches_api_response
from tools.routes import APIRoutes, AppRoute
from tools.ui_steps import ui_step


class CreateCoursePage(BasePage):
    def __init__(self, page: Page) -> None:
        """Связывает редактор курса, обложку, упражнения и состояния запросов с вкладкой."""
        super().__init__(page)
        self.navbar = NavbarComponent(page)
        self.sidebar = SidebarComponent(page)
        self.toolbar = CreateCourseToolbarViewComponent(page)
        self.form = CreateCourseFormComponent(page)
        self.image_upload_widget = ImageUploadWidgetComponent(page, "create-course-preview")
        self.exercises = CourseExercisesComponent(page)
        self.exercise_toolbar = self.exercises.toolbar
        self.exercises_empty_view = self.exercises.empty_view
        self.back_button = Button(page, "course-back-button")
        self.loading = BaseElement(page, "course-loading-status")
        self.saving = BaseElement(page, "course-saving-status")
        self.error_alert = BaseElement(page, "course-error-alert")
        self.saved_alert = BaseElement(page, "course-saved-alert")
        self.load_error_alert = BaseElement(page, "course-load-error-alert")
        self.load_retry_button = Button(page, "course-load-retry-button")
        self.preview_error_alert = BaseElement(page, "course-preview-error-alert")
        self.exercises_before_save_alert = BaseElement(page, "course-exercises-before-save-alert")
        self.exercises_loading = BaseElement(page, "course-exercises-loading-status")
        self.exercises_load_error_alert = BaseElement(page, "course-exercises-load-error-alert")
        self.exercises_retry_button = Button(page, "course-exercises-retry-button")

    @allure.step("Open course editor")
    def visit_course(self, course_id: str) -> None:
        """Открывает редактор существующего курса по UUID."""
        self.visit(AppRoute.EDIT_COURSE.format(course_id=course_id))

    def submit_new_course(self, on_cover_uploaded: Callable[[Response], None]) -> tuple[Response, Response]:
        """Сохраняет новый курс с выбранной обложкой и возвращает оба ответа.

        Форма и изображение должны быть подготовлены до вызова. Ожидания
        устанавливаются до нажатия кнопки сохранения. Ошибки обработчика
        загрузки передаются вызывающему коду.

        Args:
            on_cover_uploaded: Обработчик ответа загрузки файла. Вызывается до
                завершения ожидания курса, чтобы сразу зарегистрировать очистку.

        Returns:
            Пара ответов загрузки обложки и создания курса. Проверки статуса
            и моделей выполняет вызывающий код.

        Raises:
            playwright.sync_api.TimeoutError: Если один из ответов не получен вовремя.
        """
        with ui_step("Save new course with cover"):
            with self.page.expect_response(
                lambda response: matches_api_response(response, "POST", APIRoutes.COURSES)
            ) as course_created:
                cover_response = self._wait_for_api_response(
                    "POST", APIRoutes.FILES, self.toolbar.click_create_course_button
                )
                on_cover_uploaded(cover_response)
            return cover_response, course_created.value

    def save_course_details(self, course_id: str) -> Response:
        """Сохраняет заполненные поля существующего курса и ждёт PATCH.

        Args:
            course_id: UUID открытого в редакторе курса.

        Returns:
            Ответ PATCH курса без проверки статуса.
        """
        return self._wait_for_api_response(
            "PATCH", f"{APIRoutes.COURSES}/{course_id}", self.toolbar.click_create_course_button
        )

    def save_new_exercise(self, draft_index: int) -> Response:
        """Сохраняет выбранный черновик упражнения и ждёт его POST.

        Args:
            draft_index: Индекс черновика в идентификаторе редактора, начиная с нуля.

        Returns:
            Ответ создания упражнения без проверки статуса.
        """
        return self._wait_for_api_response(
            "POST", APIRoutes.EXERCISES, self.exercises.draft(draft_index).click_save_button
        )

    def save_existing_exercise(self, exercise_id: str) -> Response:
        """Сохраняет изменения упражнения, выбранного по UUID, и ждёт PATCH.

        Args:
            exercise_id: UUID сохранённого упражнения в открытом редакторе.

        Returns:
            Ответ обновления упражнения без проверки статуса.
        """
        return self._wait_for_api_response(
            "PATCH",
            f"{APIRoutes.EXERCISES}/{exercise_id}",
            self.exercises.saved(exercise_id).click_save_button,
        )

    @allure.step("Check exercises list is empty")
    def check_visible_exercises_empty_view(self) -> None:
        """Ожидает сообщение об отсутствии упражнений в сохранённом курсе."""
        self.exercises_empty_view.check_visible(title="No exercises yet", description="Add an exercise to this course.")
