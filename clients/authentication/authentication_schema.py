from pydantic import EmailStr, Field

from clients.base_schema import BaseSchema


class LoginRequestSchema(BaseSchema):
    """Данные учётной записи для входа через API."""

    email: EmailStr
    password: str = Field(repr=False)
