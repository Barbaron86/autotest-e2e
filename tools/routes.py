from enum import StrEnum


class AppRoute(StrEnum):
    """Маршруты страниц относительно базового адреса интерфейса."""

    LOGIN = "./#/auth/login"
    REGISTRATION = "./#/auth/registration"
    DASHBOARD = "./#/dashboard"
    COURSES = "./#/courses"
    CREATE_COURSE = "./#/courses/create"
    EDIT_COURSE = "./#/courses/{course_id}"
    PROFILE = "./#/profile"
    WELCOME = "./#/welcome"


class APIRoutes(StrEnum):
    """Корневые маршруты ресурсов API с префиксом версии."""

    USERS = "/api/v1/users"
    AUTHENTICATION = "/api/v1/authentication"
    FILES = "/api/v1/files"
    COURSES = "/api/v1/courses"
    EXERCISES = "/api/v1/exercises"
