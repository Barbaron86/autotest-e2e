import os
import sys
from typing import TYPE_CHECKING

from loguru import logger
from pydantic import BaseModel

if TYPE_CHECKING:
    from loguru import Message


_console_handler_id: int | None = None


_model_logger = logger.bind(component="MODELS", diagnostic_safe=True)


def log_model(label: str, model: BaseModel) -> None:
    """Пишет диагностическое представление типизированной модели.

    Args:
        label: Контекст модели, например запрос создания или ожидаемый курс.
        model: Модель с полями учётных данных, скрытыми через repr=False,
            если такие поля в ней есть.
    """
    _model_logger.debug("{} | {!r}", label, model)


def _write_to_stderr(message: "Message") -> None:
    """Записывает сообщение в текущий stderr и сразу сбрасывает его буфер."""
    sys.stderr.write(message)
    sys.stderr.flush()


def configure_logging() -> None:
    """Настраивает консольный Loguru-обработчик с полями компонента и воркера.

    Повторный вызов заменяет ранее созданный консольный обработчик.
    Уровень берётся из LOGURU_LEVEL, имя воркера — из PYTEST_XDIST_WORKER.
    Расширенная диагностика исключений отключена.
    """
    global _console_handler_id

    if _console_handler_id is not None:
        try:
            logger.remove(_console_handler_id)
        except ValueError:
            pass
    else:
        try:
            logger.remove(0)
        except ValueError:
            pass

    logger.configure(extra={"component": "AUTOTEST", "worker": os.getenv("PYTEST_XDIST_WORKER", "main")})
    logger.level("TRACE", icon="🔍", color="<dim>")
    logger.level("DEBUG", icon="🐛", color="<dim>")
    logger.level("INFO", icon="💡", color="<cyan>")
    logger.level("SUCCESS", icon="✅", color="<green>")
    logger.level("WARNING", icon="⚠️", color="<yellow>")
    logger.level("ERROR", icon="❌", color="<red>")
    logger.level("CRITICAL", icon="🔥", color="<bold><red>")

    _console_handler_id = logger.add(
        _write_to_stderr,
        level=os.getenv("LOGURU_LEVEL", "INFO"),
        format=(
            "<dim>{time:HH:mm:ss.SSS}</dim> | <dim>{extra[worker]}</dim> | "
            "<level>{level.icon} {level: <8}</level> | <magenta>{extra[component]: <14}</magenta> | {message}"
        ),
        colorize=sys.stderr.isatty(),
        diagnose=False,
        backtrace=False,
        enqueue=False,
    )
