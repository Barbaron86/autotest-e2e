from pydantic import BaseModel, Field

from clients.courses.courses_schema import CreateCourseRequestSchema
from clients.exercises.exercises_schema import CreateExerciseRequestSchema
from clients.users.user_schema import CreateUserRequestSchema
from tools.fakers import estimated_time, fake, max_score, min_score, unique_email


class CourseFormData(BaseModel):
    """Значения полей формы курса с генерацией тестовых данных."""

    title: str = Field(default_factory=fake.sentence)
    description: str = Field(default_factory=fake.text)
    estimated_time: str = Field(default_factory=estimated_time)
    min_score: int = Field(default_factory=min_score)
    max_score: int = Field(default_factory=max_score)

    def create_request(self, *, preview_file_id: str, created_by_user_id: str) -> CreateCourseRequestSchema:
        """Собирает API-запрос из значений, заданных для формы курса.

        Args:
            preview_file_id: ID фактически загруженной обложки.
            created_by_user_id: ID владельца создаваемого курса.

        Returns:
            Запрос со всеми полями формы и связями с файлом и владельцем.
        """
        return CreateCourseRequestSchema(
            title=self.title,
            description=self.description,
            estimated_time=self.estimated_time,
            min_score=self.min_score,
            max_score=self.max_score,
            preview_file_id=preview_file_id,
            created_by_user_id=created_by_user_id,
        )


def generate_exercise_request(course_id: str) -> CreateExerciseRequestSchema:
    """Генерирует данные упражнения указанного курса с допустимыми баллами."""
    return CreateExerciseRequestSchema(
        title=fake.sentence(),
        description=fake.sentence(nb_words=9),
        estimated_time=estimated_time(),
        min_score=min_score(),
        max_score=max_score(),
        course_id=course_id,
    )


def generate_user_request() -> CreateUserRequestSchema:
    """Генерирует запрос регистрации с уникальным email тестового аккаунта."""
    return CreateUserRequestSchema(
        email=unique_email(),
        password=fake.password(length=24),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        middle_name=fake.middle_name(),
    )
