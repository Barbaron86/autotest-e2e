import pytest
from playwright.sync_api import Page

from pages.authentication.login_page import LoginPage
from pages.authentication.registration_page import RegistrationPage
from pages.courses.courses_list_page import CoursesListPage
from pages.courses.create_course_page import CreateCoursePage
from pages.dashboard.dashboard_page import DashboardPage
from pages.profile.profile_page import ProfilePage


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """Предоставляет страницу входа без заранее подготовленной сессии."""
    return LoginPage(page)


@pytest.fixture
def registration_page(page: Page) -> RegistrationPage:
    """Предоставляет страницу регистрации без заранее подготовленной сессии."""
    return RegistrationPage(page)


@pytest.fixture
def courses_list_page(authenticated_page: Page) -> CoursesListPage:
    """Предоставляет список курсов в сессии тестового аккаунта."""
    return CoursesListPage(authenticated_page)


@pytest.fixture
def create_course_page(authenticated_page: Page) -> CreateCoursePage:
    """Предоставляет редактор курса в сессии тестового аккаунта."""
    return CreateCoursePage(authenticated_page)


@pytest.fixture
def dashboard_page(authenticated_page: Page) -> DashboardPage:
    """Предоставляет страницу статистики в сессии тестового аккаунта."""
    return DashboardPage(authenticated_page)


@pytest.fixture
def profile_page(authenticated_page: Page) -> ProfilePage:
    """Предоставляет редактор профиля в сессии тестового аккаунта."""
    return ProfilePage(authenticated_page)
