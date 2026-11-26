import allure
import pytest

from clients.courses.courses_client import CoursesClient
from clients.exercises.exercises_client import ExercisesClient
from clients.exercises.exercises_schema import GetExercisesRequestSchema
from clients.files.files_client import FilesClient
from fixtures.courses import CourseFixture
from pages.courses.courses_list_page import CoursesListPage
from testdata.factories import generate_exercise_request
from tools.assertions.course_visibility import (
    assert_course_card_removed,
    assert_course_card_visible,
    assert_course_cascade_deleted,
    assert_course_has_exercise,
    assert_delete_dialog_open,
)
from tools.routes import AppRoute

pytestmark = [pytest.mark.e2e, pytest.mark.courses]


@allure.epic("QA Course App")
@allure.feature("Courses")
class TestCourseDeletion:
    @allure.title("Delete a course and its dependent resources from the courses list")
    def test_delete_course_in_ui_cascades_to_cover_and_exercise(
        self,
        courses_list_page: CoursesListPage,
        function_course: CourseFixture,
        courses_client: CoursesClient,
        files_client: FilesClient,
        exercises_client: ExercisesClient,
    ) -> None:
        """Проверяет исчезновение курса, его обложки и упражнения после удаления в UI."""
        course = function_course.response.course
        exercise = exercises_client.create_exercise(generate_exercise_request(course.id)).exercise
        assert_course_has_exercise(
            exercises_client.get_exercises(GetExercisesRequestSchema(course_id=course.id)), course.id, exercise.id
        )
        courses_list_page.visit(AppRoute.COURSES)
        assert_course_card_visible(courses_list_page, course.id, function_course.request)

        courses_list_page.course(course.id).menu.click_delete()
        assert_delete_dialog_open(courses_list_page.delete_dialog)
        delete_response = courses_list_page.confirm_course_deletion(course.id)

        assert_course_card_removed(courses_list_page, course.id, delete_response)
        assert_course_cascade_deleted(
            course=courses_client.get_course_api(course.id),
            cover=files_client.get_file_content_api(course.preview_file.id),
            exercise=exercises_client.get_exercise_api(exercise.id),
        )
