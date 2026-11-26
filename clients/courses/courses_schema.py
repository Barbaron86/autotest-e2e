from pydantic import Field

from clients.base_schema import BaseSchema
from clients.files.files_schema import FileSchema
from clients.users.user_schema import UserSchema


class CourseSchema(BaseSchema):
    """Данные курса с обложкой и владельцем."""

    id: str
    title: str
    max_score: int | None = Field(default=None, alias="maxScore")
    min_score: int | None = Field(default=None, alias="minScore")
    description: str
    estimated_time: str | None = Field(default=None, alias="estimatedTime")
    preview_file: FileSchema = Field(alias="previewFile")
    created_by_user: UserSchema = Field(alias="createdByUser")


class GetCoursesQuerySchema(BaseSchema):
    """Параметры запроса списка курсов пользователя."""

    user_id: str = Field(alias="userId")


class GetCoursesResponseSchema(BaseSchema):
    """Ответ API со списком курсов."""

    courses: list[CourseSchema]


class GetCourseResponseSchema(BaseSchema):
    """Ответ API с одним курсом."""

    course: CourseSchema


class CreateCourseRequestSchema(BaseSchema):
    """Данные нового курса с идентификаторами обложки и владельца."""

    title: str
    max_score: int | None = Field(default=None, alias="maxScore")
    min_score: int | None = Field(default=None, alias="minScore")
    description: str
    estimated_time: str | None = Field(default=None, alias="estimatedTime")
    preview_file_id: str = Field(alias="previewFileId")
    created_by_user_id: str = Field(alias="createdByUserId")


class CreateCourseResponseSchema(BaseSchema):
    """Ответ API с созданным курсом."""

    course: CourseSchema


class UpdateCourseRequestSchema(BaseSchema):
    """Поля курса, передаваемые в запросе PATCH."""

    title: str | None = None
    description: str | None = None
    max_score: int | None = Field(default=None, alias="maxScore")
    min_score: int | None = Field(default=None, alias="minScore")
    estimated_time: str | None = Field(default=None, alias="estimatedTime")
    preview_file_id: str | None = Field(default=None, alias="previewFileId")


class UpdateCourseResponseSchema(BaseSchema):
    """Ответ API с обновлённым курсом."""

    course: CourseSchema
