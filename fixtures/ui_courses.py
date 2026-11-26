from collections.abc import Callable, Iterator
from contextlib import ExitStack
from dataclasses import dataclass

import pytest
from playwright.sync_api import Response

from clients.courses.courses_client import CoursesClient
from clients.courses.courses_schema import CreateCourseResponseSchema
from clients.files.files_client import FilesClient
from clients.files.files_schema import CreateFileResponseSchema
from fixtures.resources import CreatedCourseId, CreatedFileId, delete_owned_resource
from pages.courses.create_course_page import CreateCoursePage
from tools.assertions.course_creation import assert_browser_cover_upload_succeeded, assert_course_creation_responses


@dataclass(frozen=True)
class CourseCreation:
    uploaded: CreateFileResponseSchema
    created: CreateCourseResponseSchema
    request_body: str | None


@pytest.fixture
def save_course_with_cover(
    create_course_page: CreateCoursePage, courses_client: CoursesClient, files_client: FilesClient
) -> Iterator[Callable[[], CourseCreation]]:
    """Предоставляет сохранение курса из открытого редактора через UI.

    Обложка регистрируется на удаление сразу после загрузки. После чтения
    ID из успешного ответа фикстура регистрирует удаление курса перед
    полной проверкой ответа. Курс удаляется перед обложкой.

    Args:
        create_course_page: Редактор, который тест заполняет перед сохранением.
        courses_client: Клиент для удаления курса тестового аккаунта.
        files_client: Клиент для удаления обложки тестового аккаунта.

    Yields:
        Функция сохранения, возвращающая модели курса и файла вместе с
        телом отправленного браузером запроса.
    """
    with ExitStack() as resources:

        def register_uploaded_cover(response: Response) -> None:
            """Регистрирует удаление файла по ID сразу после успешной загрузки."""
            assert_browser_cover_upload_succeeded(response)
            uploaded = CreatedFileId.model_validate_json(response.body())
            resources.callback(delete_owned_resource, uploaded.id, files_client.delete_file_api)

        def save() -> CourseCreation:
            """Нажимает сохранение и возвращает проверенные результаты обоих запросов."""
            cover_response, course_response = create_course_page.submit_new_course(register_uploaded_cover)
            if course_response.ok:
                created = CreatedCourseId.model_validate_json(course_response.body())
                resources.callback(delete_owned_resource, created.id, courses_client.delete_course_api)
            uploaded, course = assert_course_creation_responses(cover_response, course_response)
            return CourseCreation(uploaded, course, course_response.request.post_data)

        yield save
