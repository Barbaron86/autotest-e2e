import allure
from playwright.sync_api import Locator, Page

from components.base_component import BaseComponent
from elements.button import Button
from elements.text import Text


class CreateCourseToolbarViewComponent(BaseComponent):
    def __init__(self, root: Page | Locator) -> None:
        """Связывает заголовок редактора, сохранение и причину блокировки кнопки."""
        super().__init__(root)
        self.title = Text(root, "create-course-toolbar-title-text")
        self.create_course_button = Button(root, "create-course-toolbar-create-course-button")
        self.blocked_message = Text(root, "course-save-blocked-message")

    @allure.step("Check visible course editor toolbar")
    def check_visible(self, title: str = "Create course", is_create_course_disabled: bool = True) -> None:
        """Сверяет заголовок редактора и доступность кнопки сохранения.

        Args:
            title: Ожидаемый заголовок режима создания или редактирования.
            is_create_course_disabled: Ожидается недоступная кнопка при True,
                доступная кнопка при False.
        """
        self.title.check_visible()
        self.title.check_have_text(title)
        self.create_course_button.check_visible()
        if is_create_course_disabled:
            self.create_course_button.check_disabled()
        else:
            self.create_course_button.check_enabled()

    @allure.step("Save course details")
    def click_create_course_button(self) -> None:
        """Нажимает сохранение деталей курса в текущем режиме редактора."""
        self.create_course_button.click()
