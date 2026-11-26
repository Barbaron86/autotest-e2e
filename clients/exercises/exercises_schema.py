from pydantic import Field

from clients.base_schema import BaseSchema


class ExerciseSchema(BaseSchema):
    """Данные упражнения с оценками, временем и порядком в курсе."""

    id: str
    title: str
    description: str
    course_id: str = Field(alias="courseId")
    max_score: int | None = Field(alias="maxScore")
    min_score: int | None = Field(alias="minScore")
    order_index: int = Field(default=0, alias="orderIndex")
    estimated_time: str | None = Field(alias="estimatedTime")


class GetExerciseResponseSchema(BaseSchema):
    """Ответ API с одним упражнением."""

    exercise: ExerciseSchema


class GetExercisesResponseSchema(BaseSchema):
    """Ответ API со списком упражнений."""

    exercises: list[ExerciseSchema]


class GetExercisesRequestSchema(BaseSchema):
    """Параметры запроса упражнений выбранного курса."""

    course_id: str = Field(alias="courseId")


class CreateExerciseRequestSchema(BaseSchema):
    """Данные нового упражнения и идентификатор его курса."""

    title: str
    description: str
    course_id: str = Field(alias="courseId")
    max_score: int | None = Field(alias="maxScore")
    min_score: int | None = Field(alias="minScore")
    order_index: int = Field(default=0, alias="orderIndex")
    estimated_time: str | None = Field(alias="estimatedTime")


class CreateExerciseResponseSchema(BaseSchema):
    """Ответ API с созданным упражнением."""

    exercise: ExerciseSchema


class UpdateExerciseRequestSchema(BaseSchema):
    """Поля упражнения, передаваемые в запросе PATCH."""

    title: str | None = None
    description: str | None = None
    max_score: int | None = Field(default=None, alias="maxScore")
    min_score: int | None = Field(default=None, alias="minScore")
    order_index: int | None = Field(default=None, alias="orderIndex")
    estimated_time: str | None = Field(default=None, alias="estimatedTime")


class UpdateExerciseResponseSchema(BaseSchema):
    """Ответ API с обновлённым упражнением."""

    exercise: ExerciseSchema
