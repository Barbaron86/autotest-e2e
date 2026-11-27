from collections.abc import Generator
from pathlib import Path

import allure
import pytest
from pluggy import Result
from pytest import Item, TestReport

BROWSER_ARTIFACTS_PATH = pytest.StashKey[Path]()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Item) -> Generator[None, Result[TestReport], None]:
    """Прикладывает сохранённые Playwright Trace, скриншоты и видео к Allure.

    К отчёту о teardown браузерные контексты уже закрыты и файлы сохранены.
    Allure получает файлы напрямую из каталога pytest-playwright.

    Args:
        item: Тест, для которого pytest формирует отчёт.

    Yields:
        Управление обработчикам создания отчёта pytest.
    """
    outcome = yield
    if outcome.get_result().when != "teardown" or not item.config.getoption("allure_report_dir", default=None):
        return

    output_path = item.stash.get(BROWSER_ARTIFACTS_PATH, None)
    if output_path is None:
        return

    artifact_types = {
        "trace.zip": allure.attachment_type.ZIP,
        "trace-*.zip": allure.attachment_type.ZIP,
        "test-*.png": allure.attachment_type.PNG,
        "video*.webm": allure.attachment_type.WEBM,
    }
    for pattern, attachment_type in artifact_types.items():
        for artifact in sorted(output_path.glob(pattern)):
            allure.attach.file(  # type: ignore[no-untyped-call]
                str(artifact), name=artifact.name, attachment_type=attachment_type
            )
