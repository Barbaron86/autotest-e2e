from uuid import uuid4

from faker import Faker

fake = Faker("ru_RU")


def unique_email() -> str:
    """Генерирует email с UUID для независимых тестовых аккаунтов."""
    return f"e2e-{uuid4().hex}@example.com"


def estimated_time(min_weeks: int = 1, max_weeks: int = 10) -> str:
    """Генерирует длительность в неделях из включительного диапазона.

    Args:
        min_weeks: Нижняя граница количества недель.
        max_weeks: Верхняя граница количества недель.

    Returns:
        Строка с числом недель и единицей weeks.
    """
    return f"{fake.random_int(min=min_weeks, max=max_weeks)} weeks"


def min_score() -> int:
    """Генерирует минимальный балл в диапазоне от 0 до 49 включительно."""
    return int(fake.random_int(min=0, max=49))


def max_score() -> int:
    """Генерирует максимальный балл в диапазоне от 50 до 100 включительно."""
    return int(fake.random_int(min=50, max=100))


def different_sentence(previous: str) -> str:
    """Генерирует предложение, отличающееся от исходной строки.

    При совпадении случайного значения меняет первый символ исходной строки.

    Args:
        previous: Значение, с которым новый текст должен различаться.

    Returns:
        Предложение Faker или изменённая исходная строка.
    """
    generated = str(fake.sentence())
    if generated == previous:
        prefix = "Б" if previous.startswith("А") else "А"
        return prefix + previous[1:]
    return generated
