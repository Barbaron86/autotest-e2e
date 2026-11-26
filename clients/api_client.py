from collections.abc import Mapping
from typing import Any

import allure
from httpx import URL, Client, Response


class ApiClient:
    def __init__(self, client: Client) -> None:
        """Сохраняет переданный HTTPX-клиент для запросов."""
        self.client = client

    def get(self, url: URL | str, params: Mapping[str, Any] | None = None) -> Response:
        """Выполняет GET и возвращает исходный HTTP-ответ."""
        with allure.step(f"GET {URL(url).path}"):
            return self.client.get(url, params=params)

    def post(
        self,
        url: URL | str,
        json: Any | None = None,
        data: Mapping[str, Any] | None = None,
        files: Mapping[str, Any] | None = None,
    ) -> Response:
        """Отправляет JSON, форму или файлы методом POST.

        Args:
            url: Относительный маршрут или полный URL.
            json: JSON-тело для передачи HTTPX.
            data: Поля обычной или multipart-формы.
            files: Файлы multipart-запроса в формате HTTPX.

        Returns:
            Исходный HTTP-ответ, включая ошибочный статус.
        """
        with allure.step(f"POST {URL(url).path}"):
            return self.client.post(url, json=json, data=data, files=files)

    def patch(self, url: URL | str, json: Any | None = None) -> Response:
        """Выполняет PATCH с JSON-телом и возвращает исходный ответ."""
        with allure.step(f"PATCH {URL(url).path}"):
            return self.client.patch(url, json=json)

    def delete(self, url: URL | str) -> Response:
        """Выполняет DELETE и возвращает исходный HTTP-ответ."""
        with allure.step(f"DELETE {URL(url).path}"):
            return self.client.delete(url)
