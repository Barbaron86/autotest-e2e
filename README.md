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
poetry run pytest -m e2e --alluredir=allure-results
```

Playwright сохраняет Trace каждого браузерного E2E в его каталоге в
`test-results/` при любом результате. Для одного контекста файл называется
`trace.zip`, для нескольких создаются `trace-1.zip`, `trace-2.zip` и так далее.
Скриншот и видео сохраняются при падении. При включённом Allure все сохранённые
файлы появятся во вложениях теста. Чтобы открыть архив, выполните
`poetry run playwright show-trace <путь-к-архиву>`.

Allure прикладывает исходные ZIP без изменений. В полном Trace могут быть пароли,
cookies и сетевые данные.
Проверяйте браузерные артефакты перед публикацией отчёта.

Адреса и HTTP-таймаут можно задать через `.env` по образцу
[.env.example](.env.example). По умолчанию `API_TIMEOUT` равен 100 секундам.
Прямые API-запросы используют origin из `API_BASE_URL`, а браузерный вход
идёт через UI origin. Оба адреса должны входить в `AUTH_TRUSTED_ORIGINS`
стенда. HTTPX и Playwright выполняют отдельные входы одного тестового аккаунта
и хранят cookies в своих клиентах.

## Unit-тесты инфраструктуры

Обычный запуск `poetry run pytest` исключает сценарии с маркером `unit`.
Инфраструктурные проверки запускаются из корня проекта без стенда, браузера и Allure-результатов.

```sh
poetry run pytest tests/unit -m unit --noconftest --disable-plugin-autoload
```
