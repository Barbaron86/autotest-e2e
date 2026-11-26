from http import HTTPStatus
from uuid import UUID

import allure
from httpx import Response
from loguru import logger
from playwright.sync_api import Response as BrowserResponse

from clients.courses.courses_schema import (
    CreateCourseRequestSchema,
    CreateCourseResponseSchema,
    GetCourseResponseSchema,
)
from clients.files.files_schema import CreateFileResponseSchema
from pages.courses.create_course_page import CreateCoursePage
from tools.assertions.base import assert_equal, assert_status_code
from tools.assertions.courses import assert_create_course_response
from tools.logger import log_model
from tools.routes import AppRoute

e2e_logger = logger.bind(component="E2E", diagnostic_safe=True)


def assert_browser_cover_upload_succeeded(response: BrowserResponse) -> None:
    """Проверяет успешный браузерный HTTP-ответ загрузки обложки."""
    with allure.step("Check browser uploaded the cover successfully"):
        e2e_logger.info("Check that the cover upload can proceed to course creation")
        assert response.ok, f"Cover upload failed with HTTP {response.status}."


def assert_course_creation_responses(
    cover_response: BrowserResponse, course_response: BrowserResponse
) -> tuple[CreateFileResponseSchema, CreateCourseResponseSchema]:
    """Проверяет статусы и схемы ответов загрузки обложки и создания курса.

    Args:
        cover_response: Ответ на браузерную загрузку файла.
        course_response: Ответ на браузерное создание курса.

    Returns:
        Модели ответов файла и курса с проверенными каноническими UUID.

    Raises:
        AssertionError: Если статус отличается от 200 или UUID не канонический.
        ValidationError: Если тело не соответствует схеме ответа.
        ValueError: Если идентификатор невозможно разобрать как UUID.
    """
    with allure.step("Check UI upload and course creation responses"):
        e2e_logger.info("Check the browser responses for uploading a cover and creating a course")
        assert_status_code(cover_response.status, HTTPStatus.OK)
        assert_status_code(course_response.status, HTTPStatus.OK)
        uploaded = CreateFileResponseSchema.model_validate_json(cover_response.body())
        created = CreateCourseResponseSchema.model_validate_json(course_response.body())
        assert_equal(str(UUID(uploaded.file.id)), uploaded.file.id, name="file.id")
        assert_equal(str(UUID(created.course.id)), created.course.id, name="course.id")
        return uploaded, created


def assert_course_creation_request(
    request_body: str | None, created: CreateCourseResponseSchema, expected: CreateCourseRequestSchema
) -> None:
    """Сверяет браузерный запрос и созданный курс с подготовленными данными.

    Запрос разбирается с HTTP-алиасами и запретом лишних полей.
    Сравниваются значения и набор явно переданных полей.

    Args:
        request_body: JSON-тело отправленного браузером запроса.
        created: Разобранный ответ создания курса.
        expected: Ожидаемый запрос из исходных данных сценария.

    Raises:
        AssertionError: Если тело отсутствует или проверяемые данные различаются.
        ValidationError: Если JSON запроса нарушает схему или имена полей.
    """
    with allure.step("Check course creation request and values returned by the API"):
        e2e_logger.info("Check that the browser sent the expected course fields, owner and cover")
        assert request_body is not None, "Course creation request has no body."
        actual = CreateCourseRequestSchema.model_validate_json(
            request_body, extra="forbid", by_alias=True, by_name=False
        )
        log_model("Actual browser course request", actual)
        assert_equal(actual, expected, name="course request")
        assert_equal(actual.model_fields_set, expected.model_fields_set, name="course request fields")
        assert_create_course_response(expected, created)


def assert_created_course_persisted(response: Response, course_id: str, expected: CreateCourseRequestSchema) -> None:
    """Проверяет UUID, владельца и поля курса по отдельному API-чтению.

    Args:
        response: Ответ на GET курса, выполненный после сохранения.
        course_id: UUID курса, созданного действием сценария.
        expected: Исходные данные запроса создания.

    Raises:
        AssertionError: Если статус, UUID, связи или поля курса не совпадают.
        ValidationError: Если ответ нарушает схему получения курса.
    """
    with allure.step("Check independently read course identity, owner and fields"):
        e2e_logger.info(f"Check persisted course {course_id} and its owner")
        assert_status_code(response.status_code, HTTPStatus.OK)
        saved = GetCourseResponseSchema.model_validate_json(response.content)
        assert_equal(saved.course.id, course_id, name="course.id")
        assert_create_course_response(expected, CreateCourseResponseSchema(course=saved.course))


def assert_created_cover_content(response: Response, expected: bytes) -> None:
    """Проверяет статус 200, MIME image/png и точное содержимое обложки."""
    with allure.step("Check persisted cover bytes match the selected PNG"):
        e2e_logger.info("Check stored cover content type and bytes")
        assert_status_code(response.status_code, HTTPStatus.OK)
        assert_equal(response.headers.get("content-type"), "image/png", name="cover content type")
        assert_equal(response.content, expected, name="cover content")


@allure.step("Check the editor route for created course {course_id}")
def assert_created_course_editor_url(editor: CreateCoursePage, course_id: str) -> None:
    """Проверяет маршрут редактора для UUID созданного курса."""
    e2e_logger.info(f"Check that the editor opens for course {course_id}")
    editor.check_current_url(AppRoute.EDIT_COURSE.format(course_id=course_id))


@allure.step("Check reloaded editor retains the created course and cover")
def assert_created_course_editor(editor: CreateCoursePage, course_id: str, expected: CreateCourseRequestSchema) -> None:
    """Проверяет маршрут, значения формы и загруженную обложку курса.

    Args:
        editor: Страница редактора после открытия или перезагрузки.
        course_id: UUID курса, который должен быть открыт.
        expected: Ожидаемые значения из исходных данных сценария.

    Raises:
        AssertionError: Если маршрут или состояние редактора различаются.
    """
    e2e_logger.info(f"Check form fields and loaded cover after reloading course {course_id}")
    assert_created_course_editor_url(editor, course_id)
    editor.form.check_visible(
        title=expected.title,
        description=expected.description,
        estimated_time=str(expected.estimated_time),
        min_score=str(expected.min_score),
        max_score=str(expected.max_score),
    )
    editor.image_upload_widget.check_visible(is_image_uploaded=True, is_removable=False)
