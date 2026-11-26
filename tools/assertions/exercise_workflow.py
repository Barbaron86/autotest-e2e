import allure
from loguru import logger
from playwright.sync_api import Response as BrowserResponse

from clients.courses.courses_client import CoursesClient
from clients.courses.courses_schema import (
    CourseSchema,
    GetCourseResponseSchema,
    UpdateCourseRequestSchema,
    UpdateCourseResponseSchema,
)
from clients.exercises.exercises_client import ExercisesClient
from clients.exercises.exercises_schema import (
    CreateExerciseRequestSchema,
    CreateExerciseResponseSchema,
    ExerciseSchema,
    GetExercisesRequestSchema,
)
from components.courses.create_course_exercise_form_component import CreateCourseExerciseFormComponent
from pages.courses.create_course_page import CreateCoursePage
from tools.assertions.base import assert_equal, assert_status_code
from tools.assertions.courses import assert_course, assert_update_course_response
from tools.assertions.exercises import assert_create_exercise_response, assert_exercise

logger = logger.bind(component="EXERCISE_WORKFLOW", diagnostic_safe=True)


@allure.step("Check exercise draft has no persisted record")
def assert_exercise_list_empty(client: ExercisesClient, course_id: str) -> None:
    """Через API проверяет отсутствие сохранённых упражнений у курса."""
    logger.debug("Checking draft is absent from API")
    response = client.get_exercises(GetExercisesRequestSchema(course_id=course_id))
    assert_equal(response.exercises, [], name="persisted exercises before saving")


def assert_browser_exercise_saved(
    response: BrowserResponse,
    expected: CreateExerciseRequestSchema,
    exercise_id: str | None = None,
) -> ExerciseSchema:
    """Проверяет ответ сохранения упражнения и возвращает его данные.

    Args:
        response: Ответ браузерного POST или PATCH упражнения.
        expected: Поля, введённые в редакторе до сохранения.
        exercise_id: Ожидаемый UUID при обновлении существующего упражнения.

    Returns:
        Сохранённое упражнение из проверенного ответа.

    Raises:
        AssertionError: Если статус, поля или заданный UUID не совпадают.
        ValidationError: Если ответ нарушает схему упражнения.
    """
    with allure.step("Check exercise save response"):
        assert_status_code(response.status, 200)
        saved = CreateExerciseResponseSchema.model_validate_json(response.body())
        assert_create_exercise_response(expected, saved)
        if exercise_id is not None:
            assert_equal(saved.exercise.id, exercise_id, name="saved exercise ID")
        return saved.exercise


@allure.step("Check independently persisted exercise fields")
def assert_persisted_exercise(client: ExercisesClient, exercise_id: str, expected: CreateExerciseRequestSchema) -> None:
    """Сверяет сохранённое упражнение с исходными данными через отдельный GET."""
    logger.debug("Checking stored exercise through API")
    actual = client.get_exercise(exercise_id).exercise
    expected_exercise = ExerciseSchema(id=exercise_id, **expected.model_dump(by_alias=False))
    assert_exercise(actual, expected_exercise)


def assert_course_title_persisted(
    response: BrowserResponse,
    client: CoursesClient,
    original: CourseSchema,
    expected_title: str,
) -> None:
    """Проверяет сохранение заголовка курса и сохранность остальных его полей.

    Args:
        response: Браузерный ответ обновления курса.
        client: Клиент для независимого чтения сохранённого курса.
        original: Полные данные курса до изменения заголовка.
        expected_title: Заголовок, введённый в форму до сохранения.

    Raises:
        AssertionError: Если статус, заголовок или остальные поля различаются.
        ValidationError: Если браузерный или API-ответ нарушает схему курса.
    """
    with allure.step("Check course details are saved independently"):
        assert_status_code(response.status, 200)
        saved = UpdateCourseResponseSchema.model_validate_json(response.body())
        assert_update_course_response(UpdateCourseRequestSchema(title=expected_title), saved, original)
        persisted_response = client.get_course_api(original.id)
        assert_status_code(persisted_response.status_code, 200)
        persisted = GetCourseResponseSchema.model_validate_json(persisted_response.content)
        assert_course(persisted.course, original.model_copy(update={"title": expected_title}))


@allure.step("Check saved course has an empty exercise editor")
def assert_empty_exercise_editor(page: CreateCoursePage) -> None:
    """Проверяет начальное состояние редактора без упражнений."""
    logger.debug("Checking empty exercise editor")
    page.check_visible_exercises_empty_view()


@allure.step("Check exercise save status")
def assert_exercise_save_status(exercise: CreateCourseExerciseFormComponent, expected_status: str) -> None:
    """Проверяет отображаемый статус сохранения конкретного упражнения."""
    logger.debug("Checking exercise save status")
    exercise.save_status.check_have_text(expected_status)


@allure.step("Check course and saved exercise after reload")
def assert_reloaded_exercise_editor(
    page: CreateCoursePage,
    course_title: str,
    exercise_id: str,
    expected: CreateExerciseRequestSchema,
) -> None:
    """Проверяет курс и первое сохранённое упражнение после перезагрузки.

    Args:
        page: Перезагруженная страница редактора курса.
        course_title: Ожидаемый заголовок курса.
        exercise_id: UUID сохранённого упражнения.
        expected: Поля упражнения из исходных данных сценария.

    Raises:
        AssertionError: Если поля, позиция или статус Saved не совпадают.
    """
    logger.debug("Checking persisted course and exercise in reloaded editor")
    page.form.title_input.check_have_value(course_title)
    exercise = page.exercises.saved(exercise_id)
    exercise.check_visible(
        title=expected.title,
        description=expected.description,
        estimated_time=expected.estimated_time or "",
        min_score="" if expected.min_score is None else str(expected.min_score),
        max_score="" if expected.max_score is None else str(expected.max_score),
        position=1,
    )
    assert_exercise_save_status(exercise, "Saved")
