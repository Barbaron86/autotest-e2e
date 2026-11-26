from collections.abc import Iterator
from contextlib import contextmanager

import allure
from loguru import logger

ui_logger = logger.bind(component="UI", diagnostic_safe=True)


@contextmanager
def ui_step(title: str) -> Iterator[None]:
    """Создаёт Allure-шаг и пишет его заголовок в безопасный UI-лог.

    Args:
        title: Заголовок шага без паролей, токенов и других секретов.

    Yields:
        Управление UI-действию внутри Allure-шага.
    """
    ui_logger.debug(title)
    with allure.step(title):
        yield
