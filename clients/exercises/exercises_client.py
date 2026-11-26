import allure
from httpx import Response

from clients.api_client import ApiClient
from clients.exercises.exercises_schema import (
    CreateExerciseRequestSchema,
    CreateExerciseResponseSchema,
    GetExerciseResponseSchema,
    GetExercisesRequestSchema,
    GetExercisesResponseSchema,
    UpdateExerciseRequestSchema,
    UpdateExerciseResponseSchema,
)
from clients.private_http_builder import AuthenticationUserSchema, get_private_http_client
from tools.logger import log_model
from tools.routes import APIRoutes


class ExercisesClient(ApiClient):
    @allure.step("Get exercises request")
    def get_exercises_api(self, query: GetExercisesRequestSchema) -> Response:
        """Запрашивает упражнения курса и возвращает исходный HTTP-ответ."""
        log_model("Exercises query", query)
        return self.get(APIRoutes.EXERCISES, params=query.model_dump(mode="json"))

    @allure.step("Get exercises")
    def get_exercises(self, query: GetExercisesRequestSchema) -> GetExercisesResponseSchema:
        """Получает список упражнений курса из успешного ответа.

        Args:
            query: UUID курса для фильтрации упражнений.

        Returns:
            Проверенная модель списка упражнений.

        Raises:
            httpx.HTTPStatusError: API вернул ошибочный статус.
            pydantic.ValidationError: Успешный ответ не соответствует схеме.
        """
        response = self.get_exercises_api(query)
        response.raise_for_status()
        result = GetExercisesResponseSchema.model_validate_json(response.content)
        log_model("Get exercises response", result)
        return result

    @allure.step("Create exercise request")
    def create_exercise_api(self, request: CreateExerciseRequestSchema) -> Response:
        """Отправляет модель создания упражнения и возвращает HTTP-ответ."""
        log_model("Create exercise request", request)
        return self.post(APIRoutes.EXERCISES, json=request.model_dump(mode="json"))

    @allure.step("Create exercise")
    def create_exercise(self, request: CreateExerciseRequestSchema) -> CreateExerciseResponseSchema:
        """Создаёт упражнение и разбирает успешный ответ.

        Args:
            request: Поля упражнения и UUID родительского курса.

        Returns:
            Модель ответа с созданным упражнением.

        Raises:
            httpx.HTTPStatusError: API вернул ошибочный статус.
            pydantic.ValidationError: Успешный ответ не соответствует схеме.
        """
        response = self.create_exercise_api(request)
        response.raise_for_status()
        result = CreateExerciseResponseSchema.model_validate_json(response.content)
        log_model("Create exercise response", result)
        return result

    @allure.step("Get exercise request by ID {exercise_id}")
    def get_exercise_api(self, exercise_id: str) -> Response:
        """Запрашивает упражнение по UUID и возвращает HTTP-ответ."""
        return self.get(f"{APIRoutes.EXERCISES}/{exercise_id}")

    @allure.step("Get exercise by ID {exercise_id}")
    def get_exercise(self, exercise_id: str) -> GetExerciseResponseSchema:
        """Получает упражнение по UUID из успешного ответа.

        Args:
            exercise_id: UUID запрашиваемого упражнения.

        Returns:
            Проверенная модель ответа с упражнением.

        Raises:
            httpx.HTTPStatusError: API вернул ошибочный статус.
            pydantic.ValidationError: Успешный ответ не соответствует схеме.
        """
        response = self.get_exercise_api(exercise_id)
        response.raise_for_status()
        result = GetExerciseResponseSchema.model_validate_json(response.content)
        log_model("Get exercise response", result)
        return result

    @allure.step("Update exercise request")
    def update_exercise_api(self, exercise_id: str, request: UpdateExerciseRequestSchema) -> Response:
        """Отправляет явно заданные поля PATCH упражнения.

        Пропущенные поля исключаются из JSON. Явный null и ноль сохраняются.

        Args:
            exercise_id: UUID изменяемого упражнения.
            request: Частичное изменение упражнения.

        Returns:
            Исходный HTTP-ответ, включая ошибочный статус.
        """
        log_model("Update exercise request", request)
        return self.patch(
            f"{APIRoutes.EXERCISES}/{exercise_id}",
            json=request.model_dump(mode="json", exclude_unset=True),
        )

    @allure.step("Update exercise")
    def update_exercise(self, exercise_id: str, request: UpdateExerciseRequestSchema) -> UpdateExerciseResponseSchema:
        """Изменяет упражнение и разбирает успешный ответ.

        Args:
            exercise_id: UUID изменяемого упражнения.
            request: Явно заданные поля изменения.

        Returns:
            Модель ответа с обновлённым упражнением.

        Raises:
            httpx.HTTPStatusError: API вернул ошибочный статус.
            pydantic.ValidationError: Успешный ответ не соответствует схеме.
        """
        response = self.update_exercise_api(exercise_id, request)
        response.raise_for_status()
        result = UpdateExerciseResponseSchema.model_validate_json(response.content)
        log_model("Update exercise response", result)
        return result

    @allure.step("Delete exercise request by ID {exercise_id}")
    def delete_exercise_api(self, exercise_id: str) -> Response:
        """Удаляет упражнение по UUID и возвращает исходный HTTP-ответ."""
        return self.delete(f"{APIRoutes.EXERCISES}/{exercise_id}")

    @allure.step("Delete exercise by ID {exercise_id}")
    def delete_exercise(self, exercise_id: str) -> None:
        """Удаляет упражнение и проверяет успешность HTTP-ответа.

        Args:
            exercise_id: UUID удаляемого упражнения.

        Raises:
            httpx.HTTPStatusError: API вернул ошибочный статус.
        """
        self.delete_exercise_api(exercise_id).raise_for_status()


def get_exercises_client(user: AuthenticationUserSchema) -> ExercisesClient:
    """Выполняет login и создаёт API-клиент упражнений.

    Args:
        user: Учётные данные владельца сессии.

    Returns:
        Клиент упражнений с отдельным авторизованным транспортом.
        Вызывающий код отвечает за закрытие транспорта.
    """
    return ExercisesClient(client=get_private_http_client(user))
