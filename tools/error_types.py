"""Машинные типы ошибок валидации тестируемого API."""

from enum import StrEnum


class ValidationErrorType(StrEnum):
    """Типы ошибок, используемые в ожиданиях API-тестов."""

    STRING_TYPE = "string_type"
    STRING_TOO_LONG = "string_too_long"
    STRING_TOO_SHORT = "string_too_short"
    UUID_PARSING = "uuid_parsing"
    VALUE_ERROR = "value_error"
    MISSING = "missing"
    INT_TYPE = "int_type"
    GREATER_THAN_EQUAL = "greater_than_equal"
    LESS_THAN_EQUAL = "less_than_equal"
