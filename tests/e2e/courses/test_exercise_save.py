import allure
import pytest

from clients.courses.courses_client import CoursesClient
from clients.exercises.exercises_client import ExercisesClient
from fixtures.courses import CourseFixture
from pages.courses.create_course_page import CreateCoursePage
from testdata.factories import generate_exercise_request
from tools.assertions.exercise_workflow import (
    assert_browser_exercise_saved,
    assert_course_title_persisted,
    assert_empty_exercise_editor,
    assert_exercise_list_empty,
    assert_exercise_save_status,
    assert_persisted_exercise,
    assert_reloaded_exercise_editor,
)
from tools.fakers import different_sentence, estimated_time, max_score


@pytest.mark.e2e
@pytest.mark.courses
@allure.epic("QA Course App")
@allure.feature("Exercises")
@allure.title("Save an exercise independently of course details")
def test_exercise_is_saved_separately_from_course_details(
    function_course: CourseFixture,
    create_course_page: CreateCoursePage,
    courses_client: CoursesClient,
    exercises_client: ExercisesClient,
) -> None:
    """Проверяет, что правки упражнения требуют отдельного сохранения.

    Сценарий подтверждает через API, что до первого сохранения существует
    только черновик и что сохранение курса не применяет правки упражнения.
    """
    course = function_course.response.course
    initial_exercise = generate_exercise_request(course.id).model_copy(
        update={"min_score": 0, "max_score": 0, "order_index": 0}
    )
    updated_exercise = initial_exercise.model_copy(
        update={
            "title": different_sentence(initial_exercise.title),
            "description": different_sentence(initial_exercise.description),
            "estimated_time": estimated_time(min_weeks=11, max_weeks=20),
            "max_score": max_score(),
        }
    )
    updated_course_title = different_sentence(function_course.request.title)

    create_course_page.visit_course(course.id)
    assert_empty_exercise_editor(create_course_page)
    create_course_page.exercise_toolbar.click_create_exercise_button()
    draft = create_course_page.exercises.draft(0)
    draft.fill_create_exercise_form(
        title=initial_exercise.title,
        description=initial_exercise.description,
        estimated_time=initial_exercise.estimated_time,
        min_score=str(initial_exercise.min_score),
        max_score=str(initial_exercise.max_score),
    )
    assert_exercise_save_status(draft, "Draft")
    assert_exercise_list_empty(exercises_client, course.id)

    create_response = create_course_page.save_new_exercise(draft_index=0)
    saved = assert_browser_exercise_saved(create_response, initial_exercise)
    assert_persisted_exercise(exercises_client, saved.id, initial_exercise)

    exercise = create_course_page.exercises.saved(saved.id)
    assert_exercise_save_status(exercise, "Saved")
    exercise.fill_create_exercise_form(
        title=updated_exercise.title,
        description=updated_exercise.description,
        estimated_time=updated_exercise.estimated_time,
        min_score=str(updated_exercise.min_score),
        max_score=str(updated_exercise.max_score),
    )
    assert_exercise_save_status(exercise, "Unsaved changes")
    create_course_page.form.title_input.fill(updated_course_title)
    course_response = create_course_page.save_course_details(course.id)
    assert_course_title_persisted(course_response, courses_client, course, updated_course_title)
    assert_persisted_exercise(exercises_client, saved.id, initial_exercise)
    assert_exercise_save_status(exercise, "Unsaved changes")

    update_response = create_course_page.save_existing_exercise(saved.id)
    assert_browser_exercise_saved(update_response, updated_exercise, exercise_id=saved.id)
    assert_persisted_exercise(exercises_client, saved.id, updated_exercise)

    create_course_page.reload()
    assert_reloaded_exercise_editor(create_course_page, updated_course_title, saved.id, updated_exercise)
