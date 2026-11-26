from collections.abc import Iterator
from dataclasses import dataclass

import pytest

from clients.courses.courses_client import CoursesClient
from clients.courses.courses_schema import CreateCourseRequestSchema, CreateCourseResponseSchema
from fixtures.files import FileFixture
from fixtures.resources import CreatedCourseId, clean_owned_resource
from fixtures.users import UserFixture
from testdata.factories import CourseFormData
from tools.assertions.courses import assert_create_course_response


@dataclass(frozen=True)
class CourseFixture:
    request: CreateCourseRequestSchema
    response: CreateCourseResponseSchema


@pytest.fixture
def function_course(
    courses_client: CoursesClient, function_user: UserFixture, function_file: FileFixture
) -> Iterator[CourseFixture]:
    """Готовит курс с обложкой от имени тестового аккаунта.

    Минимальный ID разбирается до проверки полной модели ответа, чтобы
    удаление курса было зарегистрировано даже при ошибке этой проверки.

    Args:
        courses_client: Клиент курсов тестового аккаунта.
        function_user: Данные владельца курса.
        function_file: Загруженная обложка владельца.

    Yields:
        Исходный запрос и проверенный ответ создания курса. После теста курс
        удаляется по ID.
    """
    request = CourseFormData(min_score=0).create_request(
        preview_file_id=function_file.response.file.id,
        created_by_user_id=function_user.response.user.id,
    )
    response = courses_client.create_course_api(request)
    response.raise_for_status()
    course_id = CreatedCourseId.model_validate_json(response.content).id
    with clean_owned_resource(course_id, courses_client.delete_course_api):
        created = CreateCourseResponseSchema.model_validate_json(response.content)
        assert_create_course_response(request, created)
        yield CourseFixture(request, created)
