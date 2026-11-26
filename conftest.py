"""Подключение фикстур и плагинов pytest для сквозных тестов."""

from tools.logger import configure_logging

pytest_plugins = (
    "tools.allure.artifacts",
    "fixtures.api",
    "fixtures.users",
    "fixtures.files",
    "fixtures.courses",
    "fixtures.browsers",
    "fixtures.pages",
    "fixtures.ui_courses",
    "tools.allure.logs",
)


def pytest_configure() -> None:
    """Настраивает логирование до сбора и запуска тестов."""
    configure_logging()
