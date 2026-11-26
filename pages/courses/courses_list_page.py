import allure
from playwright.sync_api import Page, Response

from components.courses.course_list_toolbar_view_component import (
    CourseListToolbarViewComponent,
)
from components.courses.course_view_component import CourseViewComponent
from components.courses.delete_course_dialog_component import (
    DeleteCourseDialogComponent,
)
from components.navigation.navbar_component import NavbarComponent
from components.navigation.sidebar_component import SidebarComponent
from components.views.empty_view_component import EmptyViewComponent
from elements.base_element import BaseElement
from elements.button import Button
from pages.base_page import BasePage
from tools.routes import APIRoutes, AppRoute


class CoursesListPage(BasePage):
    def __init__(self, page: Page) -> None:
        """Связывает список курсов, навигацию и диалог удаления с вкладкой."""
        super().__init__(page)
        self.navbar = NavbarComponent(page)
        self.sidebar = SidebarComponent(page)
        self.toolbar_view = CourseListToolbarViewComponent(page)
        self.empty_view = EmptyViewComponent(page, "courses-list")
        self.refresh_button = Button(page, "courses-list-refresh-button")
        self.retry_button = Button(page, "courses-list-retry-button")
        self.loading = BaseElement(page, "courses-list-loading")
        self.error_alert = BaseElement(page, "courses-list-error-alert")
        self.results = BaseElement(page, "courses-list-results")
        self.delete_dialog = DeleteCourseDialogComponent(page)

    def course(self, course_id: str) -> CourseViewComponent:
        """Возвращает компонент карточки курса, выбранной по UUID."""
        return CourseViewComponent(self.page, course_id)

    @allure.step("Open courses and receive cover {file_id}")
    def visit_with_cover(self, file_id: str) -> Response:
        """Открывает список курсов и перехватывает запрос нужной обложки.

        Args:
            file_id: UUID файла обложки, который браузер должен запросить.

        Returns:
            Ответ GET содержимого файла. Статус и байты проверяет вызывающий код.
        """
        return self._wait_for_api_response(
            "GET",
            f"{APIRoutes.FILES}/{file_id}/content",
            lambda: self.visit(AppRoute.COURSES),
        )

    @allure.step("Confirm deletion of course {course_id}")
    def confirm_course_deletion(self, course_id: str) -> Response:
        """Подтверждает удаление в уже открытом диалоге и ждёт ответ API.

        Args:
            course_id: UUID курса, выбранного для удаления.

        Returns:
            Ответ DELETE конкретного курса без проверки статуса.
        """
        return self._wait_for_api_response(
            "DELETE",
            f"{APIRoutes.COURSES}/{course_id}",
            self.delete_dialog.confirm_button.click,
        )

    @allure.step("Check courses list is empty")
    def check_visible_empty_view(self) -> None:
        """Ожидает сообщение о пустом списке курсов с заголовком и описанием."""
        self.empty_view.check_visible(title="No courses yet", description="Create a course to get started.")
