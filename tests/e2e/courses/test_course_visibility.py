import allure
import pytest

from fixtures.courses import CourseFixture
from fixtures.files import FileFixture
from pages.courses.courses_list_page import CoursesListPage
from tools.assertions.course_visibility import assert_browser_cover_response, assert_course_card_visible

pytestmark = [pytest.mark.e2e, pytest.mark.courses]


@allure.epic("QA Course App")
@allure.feature("Courses")
class TestCourseVisibility:
    @allure.title("Show an API-created course and its cover to the owner")
    def test_api_created_course_is_visible_in_ui(
        self, courses_list_page: CoursesListPage, function_course: CourseFixture, function_file: FileFixture
    ) -> None:
        """Сверяет карточку курса из API и байты обложки, полученные браузером."""
        course_id = function_course.response.course.id
        cover_response = courses_list_page.visit_with_cover(function_file.response.file.id)

        assert_browser_cover_response(cover_response, function_file.request.upload_file)
        assert_course_card_visible(courses_list_page, course_id, function_course.request)
