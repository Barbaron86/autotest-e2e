"""Подключение фикстур и плагинов pytest для сквозных тестов."""

import os
import shlex

import pytest

from tools.logger import configure_logging

pytest_plugins = (
    "tools.allure.artifacts",
    "tools.allure.environment",
    "fixtures.api",
    "fixtures.users",
    "fixtures.files",
    "fixtures.courses",
    "fixtures.browsers",
    "fixtures.pages",
    "fixtures.ui_courses",
    "tools.allure.logs",
)


def pytest_configure(config: pytest.Config) -> None:
    """Настраивает отчётность и браузерные артефакты предметного запуска."""
    configure_logging()

    config.option.attach_capture = False
    args = (*config.getini("addopts"), *shlex.split(os.getenv("PYTEST_ADDOPTS", "")), *config.invocation_params.args)
    explicit_options = {arg.partition("=")[0] for arg in args}
    browser_defaults = {"tracing": "on", "screenshot": "only-on-failure", "video": "retain-on-failure"}
    for name, default in browser_defaults.items():
        if f"--{name}" not in explicit_options and config.getoption(name, default=None) == "off":
            setattr(config.option, name, default)


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Защищает Allure-отчёт от выбора unit-тестов после фильтрации маркеров."""
    if config.getoption("allure_report_dir", default=None) and any(item.get_closest_marker("unit") for item in items):
        raise pytest.UsageError(
            "Запустите unit-тесты отдельно: pytest tests/unit -m unit --noconftest --disable-plugin-autoload"
        )
