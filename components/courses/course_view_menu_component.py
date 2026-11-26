import allure
from playwright.sync_api import Locator, Page

from components.base_component import BaseComponent
from elements.button import Button


class CourseViewMenuComponent(BaseComponent):
    def __init__(self, page: Page, card: Locator) -> None:
        """Связывает кнопку выбранной карточки и пункты её открытого меню.

        Args:
            page: Страница с меню, которое отображается вне DOM-области карточки.
            card: Локатор конкретной карточки курса.
        """
        super().__init__(card)
        self.menu_button = Button(card, "course-view-menu-button")
        menu = page.get_by_test_id("course-view-menu").filter(visible=True)
        self.edit_menu_button = Button(menu, "course-view-edit-menu-item")
        self.delete_menu_button = Button(menu, "course-view-delete-menu-item")

    @allure.step("Open course menu and edit course")
    def click_edit(self) -> None:
        """Открывает меню выбранной карточки и нажимает редактирование."""
        self.menu_button.click()
        self.edit_menu_button.click()

    @allure.step("Open course menu and delete course")
    def click_delete(self) -> None:
        """Открывает меню выбранной карточки и нажимает удаление."""
        self.menu_button.click()
        self.delete_menu_button.click()
