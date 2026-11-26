from pydantic import EmailStr, Field

from clients.base_schema import BaseSchema


class TokenSchema(BaseSchema):
    """Пара токенов авторизации и тип токена."""

    token_type: str = Field(alias="tokenType")
    access_token: str = Field(alias="accessToken", repr=False)
    refresh_token: str = Field(alias="refreshToken", repr=False)


class LoginRequestSchema(BaseSchema):
    """Данные учётной записи для входа через API."""

    email: EmailStr
    password: str = Field(repr=False)


class LoginResponseSchema(BaseSchema):
    """Ответ API входа с парой токенов."""

    token: TokenSchema


class RefreshRequestSchema(BaseSchema):
    """Запрос новой пары токенов по refresh-токену."""

    refresh_token: str = Field(alias="refreshToken", repr=False)
