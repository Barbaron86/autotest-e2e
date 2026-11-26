"""Изолированные проверки pytest-хуков безопасного логирования."""

from collections.abc import Iterator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from io import StringIO
from typing import Any, cast
from unittest.mock import Mock

import allure
import pytest
from loguru import logger
from pluggy import Result

from tools.allure import logs

pytestmark = pytest.mark.unit

_capture_protocol = contextmanager(logs.pytest_runtest_protocol)
_safe_log = logger.bind(component="UNIT", diagnostic_safe=True)


@dataclass
class LogCaptureProbe:
    """Вызовы Allure и буферы, переданные плагином в Loguru."""

    attach: Mock
    buffers: dict[int, StringIO]

    def messages(self) -> list[list[str]]:
        """Возвращает сообщения каждого вложения без оформления строк."""
        return [
            [line.rsplit(" | ", 1)[-1] for line in call.args[0].splitlines()] for call in self.attach.call_args_list
        ]

    def assert_released(self, expected_handlers: int) -> None:
        """Проверяет закрытие буферов и удаление зарегистрированных обработчиков."""
        assert len(self.buffers) == expected_handlers
        for handler_id, buffer in self.buffers.items():
            with pytest.raises(ValueError):
                logger.remove(handler_id)
            assert buffer.closed


@pytest.fixture
def capture_probe(monkeypatch: pytest.MonkeyPatch) -> Iterator[LogCaptureProbe]:
    """Наблюдает за реальными Loguru-обработчиками и заменяет запись вложений."""
    attach = Mock()
    buffers: dict[int, StringIO] = {}
    original_add = logger.add

    def track_handler(sink: StringIO, **options: Any) -> int:
        """Регистрирует обработчик и запоминает переданный ему буфер."""
        handler_id = original_add(sink, **options)
        buffers[handler_id] = sink
        return handler_id

    monkeypatch.setattr(allure, "attach", attach)
    monkeypatch.setattr(logger, "add", track_handler)
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    try:
        yield LogCaptureProbe(attach, buffers)
    finally:
        for handler_id, buffer in buffers.items():
            with suppress(ValueError):
                logger.remove(handler_id)
            buffer.close()


def _make_item(nodeid: str, *, with_allure: bool = True) -> pytest.Item:
    """Подставляет nodeid и настройку Allure, оставляя настоящий pytest stash."""
    config = Mock(spec=pytest.Config)
    config.getoption.return_value = "allure-results" if with_allure else None
    return cast(pytest.Item, Mock(spec=pytest.Item, nodeid=nodeid, config=config, stash=pytest.Stash()))


def _report(item: pytest.Item, when: str, *, outcome: str = "passed") -> None:
    """Передаёт плагину отчёт одной фазы pytest."""
    report = cast(pytest.TestReport, Mock(spec=pytest.TestReport, when=when, outcome=outcome))
    hook = logs.pytest_runtest_makereport(item)
    next(hook)
    with suppress(StopIteration):
        hook.send(Result(report, None))


class TestAllureLogPlugin:
    """Проверяет маршрутизацию логов, вложения и освобождение ресурсов."""

    @pytest.mark.parametrize("outcome", ["passed", "failed"], ids=["passed", "failed"])
    def test_attaches_all_phases_once(self, capture_probe: LogCaptureProbe, outcome: str) -> None:
        """Собирает setup, call и teardown в единственное вложение при любом исходе теста."""
        item = _make_item("unit::test_phases")

        with _capture_protocol(item):
            _safe_log.debug("setup marker")
            _report(item, "setup")
            _safe_log.info("call marker")
            _report(item, "call", outcome=outcome)
            capture_probe.attach.assert_not_called()
            _safe_log.info("teardown marker")
            _report(item, "teardown")
            _report(item, "teardown")

        assert capture_probe.messages() == [["setup marker", "call marker", "teardown marker"]]
        assert capture_probe.attach.call_args.kwargs == {
            "name": "Test log",
            "attachment_type": allure.attachment_type.TEXT,
        }
        capture_probe.assert_released(expected_handlers=1)

    def test_attaches_only_safe_records_from_current_test(self, capture_probe: LogCaptureProbe) -> None:
        """Отбрасывает записи без разрешения, с чужим nodeid и с чужим воркером."""
        item = _make_item("unit::test_filter")

        with _capture_protocol(item):
            logger.bind(component="UNIT").info("no safety flag")
            _safe_log.bind(diagnostic_safe=False).info("explicitly unsafe")
            _safe_log.bind(diagnostic_safe="true").info("wrong safety flag type")
            _safe_log.bind(test_id="unit::other").info("foreign nodeid")
            _safe_log.bind(worker="gw-other").info("foreign worker")
            _safe_log.bind(test_id=item.nodeid, worker="main").info("safe record")
            _report(item, "teardown")

        assert capture_probe.messages() == [["safe record"]]
        capture_probe.assert_released(expected_handlers=1)

    def test_isolates_overlapping_captures_by_nodeid(self, capture_probe: LogCaptureProbe) -> None:
        """Разделяет логи разных pytest nodeid даже при одновременно открытых захватах."""
        first = _make_item("unit::test_first")
        second = _make_item("unit::test_second")

        with _capture_protocol(first):
            _safe_log.info("first setup")
            with _capture_protocol(second):
                _safe_log.info("second call")
                _report(second, "teardown")
            _safe_log.info("first teardown")
            _report(first, "teardown")

        assert capture_probe.messages() == [["second call"], ["first setup", "first teardown"]]
        capture_probe.assert_released(expected_handlers=2)

    def test_isolates_same_nodeid_by_worker(
        self, capture_probe: LogCaptureProbe, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Разделяет записи двух воркеров с одним nodeid без запуска xdist."""
        first = _make_item("unit::test_shared_name")
        second = _make_item(first.nodeid)
        monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw0")

        with _capture_protocol(first):
            _safe_log.info("gw0 setup")
            monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw1")
            with _capture_protocol(second):
                _safe_log.info("gw1 call")
                _report(second, "teardown")
            _safe_log.info("gw0 teardown")
            _report(first, "teardown")

        assert capture_probe.messages() == [["gw1 call"], ["gw0 setup", "gw0 teardown"]]
        capture_probe.assert_released(expected_handlers=2)

    def test_cleans_up_an_interrupted_protocol(self, capture_probe: LogCaptureProbe) -> None:
        """Удаляет обработчик и закрывает буфер, даже если teardown-отчёта нет."""
        item = _make_item("unit::test_interrupted")

        with pytest.raises(AssertionError, match="test interrupted"), _capture_protocol(item):
            _safe_log.info("before interruption")
            raise AssertionError("test interrupted")

        capture_probe.attach.assert_not_called()
        capture_probe.assert_released(expected_handlers=1)

    def test_skips_empty_attachment(self, capture_probe: LogCaptureProbe) -> None:
        """Освобождает захват без вложения, если безопасных записей не было."""
        item = _make_item("unit::test_empty")

        with _capture_protocol(item):
            _report(item, "teardown")

        capture_probe.attach.assert_not_called()
        capture_probe.assert_released(expected_handlers=1)

    def test_run_without_allure_does_not_create_sinks(self, capture_probe: LogCaptureProbe) -> None:
        """Не регистрирует обработчики и вложения при повторных запусках без Allure."""
        for nodeid in ("unit::test_first", "unit::test_second"):
            item = _make_item(nodeid, with_allure=False)
            with _capture_protocol(item):
                _safe_log.info("run without Allure")
                _report(item, "teardown")

        capture_probe.attach.assert_not_called()
        capture_probe.assert_released(expected_handlers=0)
