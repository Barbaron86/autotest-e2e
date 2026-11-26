"""Ожидаемые сообщения об ошибках тестируемого API."""

from enum import StrEnum


class ApiErrorMessage(StrEnum):
    """Статичные бизнес-причины ошибок без отдельного машинного кода."""

    USER_NOT_FOUND = "User not found"
    COURSE_NOT_FOUND = "Course not found"
    EXERCISE_NOT_FOUND = "Exercise not found"
    FILE_NOT_FOUND = "File not found"
    INVALID_SCORE_RANGE = "Value error, max score should not be less than min score"
    INVALID_OR_EXPIRED_REFRESH_TOKEN = "Invalid or expired token"
    INVALID_CREDENTIALS = "Invalid credentials"
    USER_ALREADY_EXISTS = "User with this email already exists"
    USER_ID_MISMATCH = "userId must match the authenticated user"
    CREATED_BY_USER_ID_MISMATCH = "createdByUserId must match the authenticated user"
    INVALID_MERGED_SCORE_RANGE = "maxScore must be greater than or equal to minScore"
    FILE_IN_USE = "File is used by a course"
    USER_HAS_RESOURCES = "Delete your courses and files before deleting the account"


class ApiErrorPattern(StrEnum):
    """Статичные шаблоны бизнес-причин с переменными данными ответа."""

    USER_ALREADY_EXISTS = "User with this email already exists"
