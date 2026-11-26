from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки адресов стенда и таймаута HTTP-запросов."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ui_base_url: HttpUrl = HttpUrl("http://127.0.0.1:3000")
    api_base_url: HttpUrl = HttpUrl("http://127.0.0.1:8000")
    api_timeout: float = Field(default=100, gt=0, allow_inf_nan=False)

    @field_validator("api_base_url")
    @classmethod
    def validate_api_origin(cls, url: HttpUrl) -> HttpUrl:
        """Проверяет, что адрес API указывает на корень сервера.

        Префикс API уже задан в маршрутах клиентов.

        Args:
            url: Адрес из настройки API_BASE_URL.

        Returns:
            Проверенный адрес сервера.

        Raises:
            ValueError: Если адрес содержит дополнительный путь, имя пользователя,
                параметры запроса или фрагмент.
        """
        if url.path not in (None, "/") or any(part is not None for part in (url.username, url.query, url.fragment)):
            raise ValueError("API_BASE_URL must be the server origin; APIRoutes includes /api/v1")
        return url


settings = Settings()
