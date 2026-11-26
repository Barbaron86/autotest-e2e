import allure
from playwright.sync_api import Locator, Page

from components.base_component import BaseComponent
from components.navigation.sidebar_list_item_component import SidebarListItemComponent
from tools.routes import AppRoute


class SidebarComponent(BaseComponent):
    def __init__(self, root: Page | Locator) -> None:
        """Связывает пункты выхода, курсов и сводной страницы с областью навигации."""
        super().__init__(root)
        self.logout_list_item = SidebarListItemComponent(root, "logout")
        self.courses_list_item = SidebarListItemComponent(root, "courses")
        self.dashboard_list_item = SidebarListItemComponent(root, "dashboard")

    @allure.step("Check visible sidebar")
    def check_visible(self) -> None:
        """Ожидает видимость всех трёх пунктов боковой навигации."""
        self.logout_list_item.check_visible("Logout")
        self.courses_list_item.check_visible("Courses")
        self.dashboard_list_item.check_visible("Dashboard")

    @allure.step("Log out from sidebar")
    def click_logout(self) -> None:
        """Нажимает выход и ожидает маршрут формы входа."""
        self.logout_list_item.navigate(AppRoute.LOGIN)

    @allure.step("Open courses from sidebar")
    def click_courses(self) -> None:
        """Открывает список курсов через боковую навигацию."""
        self.courses_list_item.navigate(AppRoute.COURSES)

    @allure.step("Open dashboard from sidebar")
    def click_dashboard(self) -> None:
        """Открывает сводную страницу через боковую навигацию."""
        self.dashboard_list_item.navigate(AppRoute.DASHBOARD)
