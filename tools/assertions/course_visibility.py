from http import HTTPStatus
from pathlib import Path

import allure
from httpx import Response
from loguru import logger
from playwright.sync_api import Response as BrowserResponse

from clients.courses.courses_schema import CreateCourseRequestSchema
from clients.exercises.exercises_schema import GetExercisesResponseSchema
from components.courses.delete_course_dialog_component import DeleteCourseDialogComponent
from pages.courses.courses_list_page import CoursesListPage
from tools.assertions.base import assert_equal, assert_status_code

e2e_logger = logger.bind(component="E2E", diagnostic_safe=True)


def _display_value(value: str | int | None) -> str:
    """Преобразует необязательное значение в отображаемый карточкой текст."""
    return "Not specified" if value is None else str(value)


@allure.step("Check visible card for course {course_id}")
def assert_course_card_visible(page: CoursesListPage, course_id: str, expected: CreateCourseRequestSchema) -> None:
    """Проверяет карточку курса по UUID, её поля и загруженное изображение."""
    e2e_logger.info(f"Check rendered course fields and image for {course_id}")
    page.course(course_id).check_visible(
        title=expected.title,
        max_score=_display_value(expected.max_score),
        min_score=_display_value(expected.min_score),
        estimated_time=_display_value(expected.estimated_time),
    )


def assert_browser_cover_response(response: BrowserResponse, expected_file: Path) -> None:
    """Сверяет статус, MIME и байты браузерной обложки с исходным PNG."""
    with allure.step("Check the cover served to the browser"):
        e2e_logger.info("Check protected cover response type and bytes against the uploaded sample")
        assert_status_code(response.status, HTTPStatus.OK)
        assert_equal(response.header_value("content-type"), "image/png", "cover MIME type")
        assert_equal(response.body(), expected_file.read_bytes(), "cover contents")


@allure.step("Check the course contains exercise {exercise_id} before deletion")
def assert_course_has_exercise(response: GetExercisesResponseSchema, course_id: str, exercise_id: str) -> None:
    """Проверяет единственное упражнение курса перед его удалением.

    Args:
        response: API-список упражнений подготовленного курса.
        course_id: UUID курса, которому должно принадлежать упражнение.
        exercise_id: UUID подготовленного упражнения.

    Raises:
        AssertionError: Если состав списка или связь с курсом отличаются.
    """
    e2e_logger.info(f"Check that exercise {exercise_id} belongs to course {course_id}")
    assert_equal(
        [(exercise.id, exercise.course_id) for exercise in response.exercises],
        [(exercise_id, course_id)],
        "exercises of the course before deletion",
    )


@allure.step("Check course deletion confirmation is open")
def assert_delete_dialog_open(dialog: DeleteCourseDialogComponent) -> None:
    """Проверяет видимость диалога подтверждения удаления курса."""
    e2e_logger.info("Check the delete confirmation dialog is visible")
    dialog.check_visible()


def assert_course_card_removed(page: CoursesListPage, course_id: str, response: BrowserResponse) -> None:
    """Проверяет статус удаления, закрытие диалога и исчезновение нужной карточки."""
    with allure.step("Check successful UI deletion"):
        e2e_logger.info(f"Check the delete response and disappearance of course {course_id}")
        assert_status_code(response.status, HTTPStatus.OK)
        page.delete_dialog.check_hidden()
        page.course(course_id).check_hidden()


@allure.step("Check course and dependent resources are absent from the API")
def assert_course_cascade_deleted(course: Response, cover: Response, exercise: Response) -> None:
    """Проверяет ответы 404 для удалённого курса, обложки и упражнения."""
    e2e_logger.info("Check independent GET responses for the deleted course, its cover and exercise")
    assert_status_code(course.status_code, HTTPStatus.NOT_FOUND)
    assert_status_code(cover.status_code, HTTPStatus.NOT_FOUND)
    assert_status_code(exercise.status_code, HTTPStatus.NOT_FOUND)
