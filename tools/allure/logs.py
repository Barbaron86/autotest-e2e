import os
from collections.abc import Generator
from dataclasses import dataclass
from io import StringIO
from typing import TYPE_CHECKING

import allure
import pytest
from loguru import logger
from pluggy import Result
from pytest import Item, TestReport

if TYPE_CHECKING:
    from loguru import Record


_ALLURE_LOG_FORMAT = (
    "{time:HH:mm:ss.SSS} | {extra[worker]} | {level.icon} {level: <8} | {extra[component]: <14} | {message}"
)


@dataclass(frozen=True, slots=True)
class _LogCapture:
    buffer: StringIO
    handler_id: int


_LOG_CAPTURE_KEY = pytest.StashKey[_LogCapture]()


def _stop_log_capture(item: Item) -> str | None:
    """Останавливает захват лога теста и освобождает его буфер.

    Args:
        item: Тест с зарегистрированным обработчиком в pytest stash.

    Returns:
        Накопленный текст или None, если захват уже завершён либо не включён.
    """
    capture = item.stash.get(_LOG_CAPTURE_KEY, None)
    if capture is None:
        return None

    del item.stash[_LOG_CAPTURE_KEY]
    try:
        logger.remove(capture.handler_id)
        return capture.buffer.getvalue()
    finally:
        capture.buffer.close()


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_protocol(item: Item) -> Generator[None, object, None]:
    """Связывает Loguru-записи с текущим тестом и собирает безопасный лог.

    При заданном каталоге Allure сохраняет записи с diagnostic_safe=True,
    совпадающими nodeid и воркером. Обработчик и буфер освобождаются
    после завершения протокола даже при ошибке теста.

    Args:
        item: Выполняемый pytest-тест.

    Yields:
        Управление оставшимся обработчикам протокола pytest.
    """
    worker = os.getenv("PYTEST_XDIST_WORKER", "main")
    with logger.contextualize(test_id=item.nodeid, worker=worker):
        if not item.config.getoption("allure_report_dir", default=None):
            yield
            return

        def belongs_to_test(record: "Record") -> bool:
            """Отбирает безопасные записи текущего теста и текущего воркера."""
            extra = record["extra"]
            return (
                extra.get("test_id") == item.nodeid
                and extra.get("worker") == worker
                and extra.get("diagnostic_safe") is True
            )

        buffer = StringIO()
        item.stash[_LOG_CAPTURE_KEY] = _LogCapture(
            buffer=buffer,
            handler_id=logger.add(
                buffer,
                level="DEBUG",
                filter=belongs_to_test,
                format=_ALLURE_LOG_FORMAT,
                colorize=False,
                diagnose=False,
                backtrace=False,
                enqueue=False,
            ),
        )
        try:
            yield
        finally:
            _stop_log_capture(item)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Item) -> Generator[None, Result[TestReport], None]:
    """Прикладывает безопасный лог к Allure после teardown теста.

    Args:
        item: Тест, отчёт которого формирует pytest.

    Yields:
        Управление обработчикам создания отчёта pytest.
    """
    outcome = yield
    report = outcome.get_result()
    if report.when != "teardown":
        return

    test_log = _stop_log_capture(item)
    if test_log:
        allure.attach(test_log, name="Test log", attachment_type=allure.attachment_type.TEXT)
