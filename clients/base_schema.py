from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Базовая модель API со строгой валидацией и псевдонимами полей."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, strict=True, hide_input_in_errors=True)
