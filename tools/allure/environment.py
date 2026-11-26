import platform
from pathlib import Path

import pytest


def pytest_sessionfinish(session: pytest.Session) -> None:
    """Записывает выбранные метаданные среды в предметный отчёт Allure.

    Файл записывает основной процесс pytest после прогона с Allure.

    Args:
        session: Завершившаяся сессия pytest.
    """
    config = session.config
    report_dir = config.getoption("allure_report_dir", default=None)
    if not report_dir or config.option.collectonly or not session.testscollected or hasattr(config, "workerinput"):
        return

    browsers = config.getoption("browser", default=[]) or ["chromium"]
    properties = {
        "os": platform.system(),
        "python_version": platform.python_version(),
        "browser": ", ".join(browsers),
    }
    path = config.invocation_params.dir / Path(report_dir) / "environment.properties"
    path.write_text("".join(f"{key}={value}\n" for key, value in properties.items()), encoding="utf-8")
