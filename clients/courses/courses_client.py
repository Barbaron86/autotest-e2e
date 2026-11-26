import allure
from httpx import Response

from clients.api_client import ApiClient
from clients.courses.courses_schema import (
    CreateCourseRequestSchema,
    CreateCourseResponseSchema,
    GetCoursesQuerySchema,
    UpdateCourseRequestSchema,
)
from clients.private_http_builder import AuthenticationUserSchema, get_private_http_client
from tools.logger import log_model
from tools.routes import APIRoutes


class CoursesClient(ApiClient):
    @allure.step("Get courses")
    def get_courses_api(self, query: GetCoursesQuerySchema) -> Response:
        """Запрашивает курсы выбранного пользователя и возвращает HTTP-ответ."""
        log_model("Course query", query)
        return self.get(APIRoutes.COURSES, params=query.model_dump(mode="json"))

    @allure.step("Get course by ID {course_id}")
    def get_course_api(self, course_id: str) -> Response:
        """Запрашивает курс по UUID и возвращает исходный HTTP-ответ."""
        return self.get(f"{APIRoutes.COURSES}/{course_id}")

    @allure.step("Create course request")
    def create_course_api(self, request: CreateCourseRequestSchema) -> Response:
        """Отправляет модель создания курса и возвращает HTTP-ответ."""
        log_model("Create course request", request)
        return self.post(APIRoutes.COURSES, json=request.model_dump(mode="json"))

    @allure.step("Create course")
    def create_course(self, request: CreateCourseRequestSchema) -> CreateCourseResponseSchema:
        """Создаёт курс и разбирает успешный ответ.

        Args:
            request: Поля курса, UUID обложки и UUID владельца.

        Returns:
            Модель ответа с созданным курсом.

        Raises:
            httpx.HTTPStatusError: API вернул ошибочный статус.
            pydantic.ValidationError: Успешный ответ не соответствует схеме.
        """
        response = self.create_course_api(request)
        response.raise_for_status()
        result = CreateCourseResponseSchema.model_validate_json(response.content)
        log_model("Create course response", result)
        return result

    @allure.step("Update course")
    def update_course_api(self, course_id: str, request: UpdateCourseRequestSchema) -> Response:
        """Отправляет явно заданные поля PATCH курса.

        Пропущенные поля исключаются из JSON. Явный null и ноль сохраняются.

        Args:
            course_id: UUID изменяемого курса.
            request: Частичное изменение курса.

        Returns:
            Исходный HTTP-ответ, включая ошибочный статус.
        """
        log_model("Update course request", request)
        return self.patch(f"{APIRoutes.COURSES}/{course_id}", json=request.model_dump(mode="json", exclude_unset=True))

    @allure.step("Delete course by ID {course_id}")
    def delete_course_api(self, course_id: str) -> Response:
        """Удаляет курс по UUID и возвращает исходный HTTP-ответ."""
        return self.delete(f"{APIRoutes.COURSES}/{course_id}")


def get_courses_client(user: AuthenticationUserSchema) -> CoursesClient:
    """Выполняет login и создаёт API-клиент курсов.

    Args:
        user: Учётные данные владельца сессии.

    Returns:
        Клиент курсов с отдельным авторизованным транспортом.
        Вызывающий код отвечает за закрытие транспорта.
    """
    return CoursesClient(client=get_private_http_client(user))
