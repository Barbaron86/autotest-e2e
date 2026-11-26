from pydantic import EmailStr, Field

from clients.base_schema import BaseSchema


class UserSchema(BaseSchema):
    """Данные пользователя, возвращаемые API."""

    id: str
    email: EmailStr
    last_name: str = Field(alias="lastName")
    first_name: str = Field(alias="firstName")
    middle_name: str = Field(alias="middleName")


class UpdateUserRequestSchema(BaseSchema):
    """Поля профиля, передаваемые в запросе PATCH."""

    email: EmailStr | None = None
    last_name: str | None = Field(default=None, alias="lastName")
    first_name: str | None = Field(default=None, alias="firstName")
    middle_name: str | None = Field(default=None, alias="middleName")


class UpdateUserResponseSchema(BaseSchema):
    """Ответ API с обновлённым профилем."""

    user: UserSchema


class GetUserResponseSchema(BaseSchema):
    """Ответ API с запрошенным пользователем."""

    user: UserSchema


class CreateUserRequestSchema(BaseSchema):
    """Данные для регистрации пользователя."""

    email: EmailStr
    password: str = Field(repr=False)
    last_name: str = Field(alias="lastName")
    first_name: str = Field(alias="firstName")
    middle_name: str = Field(alias="middleName")


class CreateUserResponseSchema(BaseSchema):
    """Ответ API с созданным пользователем."""

    user: UserSchema
