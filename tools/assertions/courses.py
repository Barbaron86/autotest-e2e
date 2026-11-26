from typing import Any

import allure

from clients.courses.courses_schema import (
    CourseSchema,
    CreateCourseRequestSchema,
    CreateCourseResponseSchema,
    GetCoursesResponseSchema,
    UpdateCourseRequestSchema,
    UpdateCourseResponseSchema,
)
from clients.error_schema import InternalErrorResponseSchema, ValidationErrorResponseSchema
from tools.assertions.base import assert_equal, assert_lens
from tools.assertions.errors import (
    ValidationErrorExpectation,
    assert_internal_error_response,
    assert_invalid_uuid_response,
    assert_validation_error_response,
)
from tools.assertions.files import assert_file
from tools.assertions.users import assert_user
from tools.error_messages import ApiErrorMessage
from tools.error_types import ValidationErrorType
from tools.logger import log_model


@allure.step("Check non-null optional course fields")
def assert_course_optional_fields_are_set(course: CourseSchema) -> None:
    """Проверяет непустое исходное состояние полей перед их очисткой."""
    for field in ("max_score", "min_score", "estimated_time"):
        assert getattr(course, field) is not None, f"Initial course field {field} must not be null"


def assert_course_with_cleared_optional_fields(actual: dict[str, Any], original_course: CourseSchema) -> None:
    """Проверяет явные null в JSON и неизменность остальных данных курса."""
    with allure.step("Check course with cleared optional fields"):
        raw_course = actual["course"]
        for field in ("maxScore", "minScore", "estimatedTime"):
            assert field in raw_course, f"Missing course field: {field}"
            assert raw_course[field] is None, f"Course field {field} must be null"
        expected_course = original_course.model_copy(
            update={"max_score": None, "min_score": None, "estimated_time": None}
        )
        assert_course(actual=CourseSchema.model_validate(raw_course), expected=expected_course)


def assert_update_course_with_invalid_score_range_response(
    actual: ValidationErrorResponseSchema | InternalErrorResponseSchema, request: UpdateCourseRequestSchema
) -> None:
    """Проверяет отказ PATCH с недопустимой парой баллов.

    При двух заданных баллах ожидает ошибку валидации тела. При одном
    заданном балле ожидает отказ после проверки пары с сохранённым значением.

    Args:
        actual: Ответ API с ошибкой валидации или бизнес-причиной отказа.
        request: Исходный PATCH-запрос.

    Raises:
        AssertionError: Если вид или содержимое ошибки не совпадают.
    """
    with allure.step("Check invalid score range response"):
        if request.max_score is not None and request.min_score is not None:
            assert isinstance(actual, ValidationErrorResponseSchema), "Expected structured payload validation error."
            expected = [
                ValidationErrorExpectation(
                    type=ValidationErrorType.VALUE_ERROR,
                    location=["body"],
                    input=request.model_dump(mode="json", exclude_unset=True),
                    context={"error": {}},
                    message=ApiErrorMessage.INVALID_SCORE_RANGE,
                )
            ]
            assert_validation_error_response(actual=actual, expected=expected)
        else:
            assert isinstance(actual, InternalErrorResponseSchema), "Expected merged score pair rejection."
            assert_equal(actual.detail, ApiErrorMessage.INVALID_MERGED_SCORE_RANGE, name="detail")


@allure.step("Check create course response")
def assert_create_course_response(request: CreateCourseRequestSchema, response: CreateCourseResponseSchema) -> None:
    """Проверяет соответствие созданного курса исходному запросу.

    Args:
        request: Данные запроса на создание курса.
        response: Ответ API с данными созданного курса.

    Raises:
        AssertionError: Если поля курса или идентификаторы вложенных
            файла превью и автора не совпадают с данными запроса.
    """
    log_model("Expected course request", request)
    log_model("Actual create course response", response)
    assert_equal(response.course.title, request.title, name="title")
    assert_equal(response.course.max_score, request.max_score, name="max_score")
    assert_equal(response.course.min_score, request.min_score, name="min_score")
    assert_equal(response.course.description, request.description, name="description")
    assert_equal(response.course.estimated_time, request.estimated_time, name="estimated_time")
    assert_equal(response.course.preview_file.id, request.preview_file_id, name="preview_file_id")
    assert_equal(response.course.created_by_user.id, request.created_by_user_id, name="created_by_user_id")


@allure.step("Check update course response")
def assert_update_course_response(
    request: UpdateCourseRequestSchema,
    response: UpdateCourseResponseSchema,
    original_course: CourseSchema | None = None,
) -> None:
    """Проверяет явно изменённые поля и при наличии исходных данных остальные.

    Args:
        request: PATCH-запрос с заданными полями, включая явный None.
        response: Ответ API после обновления курса.
        original_course: Исходный курс для проверки UUID, связей и всех
            остальных полей, отсутствовавших в запросе.

    Raises:
        AssertionError: Если изменённые или сохраняемые поля различаются.
    """
    log_model("Expected course update", request)
    log_model("Actual update course response", response)
    changes = request.model_dump(mode="json", exclude_unset=True, by_alias=False)
    for name, expected in changes.items():
        actual = response.course.preview_file.id if name == "preview_file_id" else getattr(response.course, name)
        assert_equal(actual, expected, name=name)
    if original_course is not None:
        assert_equal(response.course.id, original_course.id, name="id")
        assert_user(actual=response.course.created_by_user, expected=original_course.created_by_user)
        if "preview_file_id" not in changes:
            assert_file(actual=response.course.preview_file, expected=original_course.preview_file)
        for name in ("title", "description", "max_score", "min_score", "estimated_time"):
            if name not in changes:
                assert_equal(getattr(response.course, name), getattr(original_course, name), name=name)


@allure.step("Check course")
def assert_course(actual: CourseSchema, expected: CourseSchema) -> None:
    """Проверяет все поля курса, включая файл превью и автора.

    Args:
        actual: Фактические данные курса из ответа API.
        expected: Ожидаемые данные курса.

    Raises:
        AssertionError: Если хотя бы одно поле курса или вложенных
            файла превью и автора не соответствует ожиданиям.
    """
    log_model("Actual course", actual)
    log_model("Expected course", expected)
    assert_equal(actual.id, expected.id, name="id")
    assert_equal(actual.title, expected.title, name="title")
    assert_equal(actual.max_score, expected.max_score, name="max_score")
    assert_equal(actual.min_score, expected.min_score, name="min_score")
    assert_equal(actual.description, expected.description, name="description")
    assert_equal(actual.estimated_time, expected.estimated_time, name="estimated_time")
    assert_file(actual=actual.preview_file, expected=expected.preview_file)
    assert_user(actual=actual.created_by_user, expected=expected.created_by_user)


@allure.step("Check get courses response")
def assert_get_courses_response(
    get_courses_response: GetCoursesResponseSchema, create_course_responses: list[CreateCourseResponseSchema]
) -> None:
    """Проверяет список курсов по ответам на их создание.

    Args:
        get_courses_response: Ответ API на запрос списка курсов.
        create_course_responses: Ожидаемые ответы на создание курсов
            в порядке их получения в списке.

    Raises:
        AssertionError: Если количество, порядок или данные курсов
            не соответствуют ожидаемым значениям.
    """
    assert_lens(get_courses_response.courses, create_course_responses, name="courses")
    for index, create_course_response in enumerate(create_course_responses):
        assert_course(actual=get_courses_response.courses[index], expected=create_course_response.course)


def assert_course_not_found_response(actual: InternalErrorResponseSchema) -> None:
    """Проверяет сообщение API об отсутствии курса.

    Args:
        actual: Фактический ответ API с сообщением об ошибке.

    Raises:
        AssertionError: Если сообщение не соответствует ошибке отсутствия курса.
    """
    with allure.step("Check course not found response"):
        expected = InternalErrorResponseSchema(detail=ApiErrorMessage.COURSE_NOT_FOUND)
        assert_internal_error_response(actual=actual, expected=expected)


def assert_get_courses_with_invalid_user_id_response(actual: ValidationErrorResponseSchema, user_id: str) -> None:
    """Проверяет ошибку валидации UUID пользователя при получении курсов.

    Args:
        actual: Фактический ответ API с ошибками валидации.
        user_id: Некорректный идентификатор пользователя.

    Raises:
        AssertionError: Если ошибка не соответствует ожидаемой.
    """
    with allure.step("Check get courses with invalid user ID response"):
        assert_invalid_uuid_response(actual=actual, invalid_id=user_id, location=["query", "userId"])


def assert_course_with_invalid_id_response(actual: ValidationErrorResponseSchema, course_id: str) -> None:
    """Проверяет ошибку валидации некорректного UUID курса.

    Args:
        actual: Фактический ответ API с ошибками валидации.
        course_id: Некорректный UUID из path-параметра.

    Raises:
        AssertionError: Если ошибка не соответствует ожидаемым значениям.
    """
    with allure.step("Check course with invalid ID response"):
        assert_invalid_uuid_response(actual=actual, invalid_id=course_id, location=["path", "course_id"])


def assert_create_course_with_invalid_preview_file_id_response(
    actual: ValidationErrorResponseSchema, preview_file_id: str
) -> None:
    """Проверяет ошибку валидации UUID файла превью при создании курса.

    Args:
        actual: Фактический ответ API с ошибками валидации.
        preview_file_id: Некорректный UUID файла превью из тела запроса.

    Raises:
        AssertionError: Если ошибка не соответствует ожидаемым значениям.
    """
    with allure.step("Check create course with invalid preview file ID response"):
        assert_invalid_uuid_response(actual=actual, invalid_id=preview_file_id, location=["body", "previewFileId"])
