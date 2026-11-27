from http import HTTPStatus

import pytest
from httpx import Response

from tools.assertions.authentication import assert_logout_response

pytestmark = pytest.mark.unit


def _logout_response(access_path: str, refresh_path: str) -> Response:
    """Создаёт ответ Logout с заголовками для удаления двух cookies."""
    return Response(
        HTTPStatus.NO_CONTENT,
        headers=[
            ("Set-Cookie", f"access_token=; Max-Age=0; Path={access_path}"),
            ("Set-Cookie", f"refresh_token=; Max-Age=0; Path={refresh_path}"),
        ],
    )


class TestLogoutResponse:
    """Проверяет контракт удаления cookies при Logout."""

    def test_accepts_cookies_deleted_at_original_paths(self) -> None:
        """Принимает удаление обеих cookies с путями из контракта."""
        assert_logout_response(_logout_response("/api/v1", "/api/v1/authentication"))

    @pytest.mark.parametrize(
        ("access_path", "refresh_path"),
        [
            pytest.param("/", "/api/v1/authentication", id="incorrect-access-path"),
            pytest.param("/api/v1", "/api/v1", id="incorrect-refresh-path"),
        ],
    )
    def test_rejects_cookies_deleted_at_incorrect_paths(self, access_path: str, refresh_path: str) -> None:
        """Отклоняет удаление любой из cookies по неверному пути даже с Max-Age=0."""
        with pytest.raises(AssertionError, match="session cookies removed"):
            assert_logout_response(_logout_response(access_path, refresh_path))

    @pytest.mark.parametrize(
        ("access_cookie", "refresh_cookie"),
        [
            pytest.param(
                "access_token=; Max-Age=3600; Path=/api/v1",
                "refresh_token=; Max-Age=0; Path=/api/v1/authentication",
                id="access-max-age-nonzero",
            ),
            pytest.param(
                "access_token=; Max-Age=0; Path=/api/v1",
                "refresh_token=; Path=/api/v1/authentication",
                id="refresh-max-age-missing",
            ),
        ],
    )
    def test_rejects_cookies_without_zero_max_age(self, access_cookie: str, refresh_cookie: str) -> None:
        """Отклоняет ответ Logout с ненулевым или пропущенным Max-Age."""
        response = Response(
            HTTPStatus.NO_CONTENT,
            headers=[("Set-Cookie", access_cookie), ("Set-Cookie", refresh_cookie)],
        )

        with pytest.raises(AssertionError, match="session cookies removed"):
            assert_logout_response(response)
