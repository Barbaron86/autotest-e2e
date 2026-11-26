from collections.abc import Mapping
from typing import Any

import allure
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError


def validate_json_schema(instance: Any, schema: Mapping[str, Any]) -> None:
    """Проверяет сырой JSON по схеме Draft 2020-12 с проверкой форматов.

    Args:
        instance: Исходное JSON-значение до разбора прикладной моделью.
        schema: Ожидаемая JSON Schema.

    Raises:
        AssertionError: Если данные или сама схема невалидны. Сообщение
            содержит путь и правило без исходного JSON.
    """
    with allure.step("Validate JSON schema"):
        try:
            Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(instance)
        except ValidationError as error:
            path = ".".join(str(part) for part in error.absolute_path) or "<root>"
            raise AssertionError(f"JSON schema mismatch at {path}, rule {error.validator}.") from None
        except SchemaError:
            raise AssertionError("The expected JSON schema is invalid.") from None
