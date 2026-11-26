# Autotest E2E

Проект для сквозных UI- и API-проверок `qa-course-app`. Стенд объединяет учебные приложения Никиты Филонова.

## Локальный запуск

Из каталога `qa-course-app` запустите стенд.

```sh
docker compose up -d --build --wait
```

UI доступен по адресу `http://127.0.0.1:3000`, API — `http://127.0.0.1:8000/api/v1`.

В каталоге `autotest-e2e` с Python 3.12+ и Poetry выполните следующие команды.

```sh
poetry install
poetry run playwright install chromium
```

Запустите тесты с результатами Allure.

```sh
poetry run pytest --alluredir=allure-results
```

При падении браузерного сценария Playwright оставляет скриншот и видео в
`test-results/`. Если включён Allure, оба файла появятся и во вложениях теста.
Перед публикацией результатов проверьте, что в кадрах нет учётных данных.

Адреса и HTTP-таймаут можно задать через `.env` по образцу
[.env.example](.env.example). По умолчанию `API_TIMEOUT` равен 100 секундам.
