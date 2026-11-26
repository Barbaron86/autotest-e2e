from collections.abc import Sized
from typing import Any

import allure


@allure.step("Check response status equals {expected}")
def assert_status_code(actual: int, expected: int) -> None:
    """Проверяет HTTP-статус и сообщает ожидаемое и фактическое значения."""
    assert actual == expected, f"Incorrect status code. Expected {expected}, got {actual}."


def assert_equal(actual: Any, expected: Any, name: str) -> None:
    """Проверяет равенство значений с учётом типов JSON-чисел и bool.

    Словари и списки сравниваются рекурсивно. Сообщение ошибки содержит
    имя поля и скрывает сами сравниваемые значения.

    Args:
        actual: Фактическое значение.
        expected: Ожидаемое значение.
        name: Безопасное имя проверяемого поля.

    Raises:
        AssertionError: Если значение или проверяемый тип не совпадает.
    """
    with allure.step("Check expected field value"):
        assert _values_match(actual, expected), f"Incorrect value or type for {name}."


def _values_match(actual: Any, expected: Any) -> bool:
    """Сравнивает вложенные коллекции и различает типы int, float и bool."""
    if type(expected) in (int, float, bool):
        return type(actual) is type(expected) and actual == expected
    if isinstance(expected, dict):
        return (
            isinstance(actual, dict)
            and actual.keys() == expected.keys()
            and all((_values_match(actual[key], value) for key, value in expected.items()))
        )
    if isinstance(expected, list):
        return (
            isinstance(actual, list)
            and len(actual) == len(expected)
            and all(
                (
                    _values_match(actual_value, expected_value)
                    for actual_value, expected_value in zip(actual, expected, strict=True)
                )
            )
        )
    return bool(actual == expected)


def assert_is_true(actual: Any, name: str) -> None:
    """Проверяет истинность условия и указывает его безопасное имя при ошибке."""
    with allure.step("Check condition"):
        assert actual, f"Condition failed for {name}."


def assert_lens(actual: Sized, expected: Sized, name: str) -> None:
    """Проверяет равенство длин двух коллекций."""
    with allure.step("Check collection length"):
        assert len(actual) == len(expected), (
            f"Incorrect length for {name}. Expected {len(expected)}, got {len(actual)}."
        )
