from collections.abc import Callable
from pathlib import Path

import allure
import pytest

from clients.courses.courses_client import CoursesClient
from clients.files.files_client import FilesClient
from fixtures.ui_courses import CourseCreation
from fixtures.users import UserFixture
from pages.courses.create_course_page import CreateCoursePage
from testdata.factories import CourseFormData
from tools.assertions.course_creation import (
    assert_course_creation_request,
    assert_created_course_editor,
    assert_created_course_editor_url,
    assert_created_course_persisted,
    assert_created_cover_content,
)
from tools.routes import AppRoute

pytestmark = [pytest.mark.e2e, pytest.mark.courses]


@allure.epic("QA Course App")
@allure.feature("Courses")
@allure.title("Create a course with its cover through UI and verify API persistence")
def test_create_course_with_cover_through_ui(
    create_course_page: CreateCoursePage,
    function_user: UserFixture,
    cover_image: Path,
    courses_client: CoursesClient,
    files_client: FilesClient,
    save_course_with_cover: Callable[[], CourseCreation],
) -> None:
    """Проверяет через API и перезагрузку редактора курс, созданный в UI."""
    course_data = CourseFormData(min_score=0)

    create_course_page.visit(AppRoute.CREATE_COURSE)
    create_course_page.form.fill(
        title=course_data.title,
        description=course_data.description,
        estimated_time=course_data.estimated_time,
        min_score=str(course_data.min_score),
        max_score=str(course_data.max_score),
    )
    create_course_page.image_upload_widget.upload_preview_image(cover_image)

    result = save_course_with_cover()
    course_id = result.created.course.id
    file_id = result.uploaded.file.id
    expected = course_data.create_request(
        preview_file_id=file_id,
        created_by_user_id=function_user.response.user.id,
    )

    assert_course_creation_request(result.request_body, result.created, expected)
    assert_created_course_persisted(courses_client.get_course_api(course_id), course_id, expected)
    assert_created_cover_content(files_client.get_file_content_api(file_id), cover_image.read_bytes())

    assert_created_course_editor_url(create_course_page, course_id)
    create_course_page.reload()
    assert_created_course_editor(create_course_page, course_id, expected)
