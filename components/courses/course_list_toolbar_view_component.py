import allure
from playwright.sync_api import Locator, Page

from components.base_component import BaseComponent
from elements.button import Button
from elements.text import Text
from tools.routes import AppRoute


class CourseListToolbarViewComponent(BaseComponent):
    def __init__(self, root: Page | Locator) -> None:
        """Связывает заголовок списка курсов и кнопку создания с корневой областью."""
        super().__init__(root)
        self.title = Text(root, "courses-list-toolbar-title-text")
        self.create_course_button = Button(root, "courses-list-toolbar-create-course-button")

    @allure.step("Check visible courses list toolbar")
    def check_visible(self) -> None:
        """Ожидает заголовок списка курсов и видимую кнопку создания."""
        self.title.check_visible()
        self.title.check_have_text("Courses")
        self.create_course_button.check_visible()

    @allure.step("Open create course editor")
    def click_create_course_button(self) -> None:
        """Открывает создание курса и ожидает маршрут нового редактора."""
        self.create_course_button.click()
        self.check_current_url(AppRoute.CREATE_COURSE)
