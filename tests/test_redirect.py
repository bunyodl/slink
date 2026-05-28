from datetime import UTC, datetime

from fastapi.testclient import TestClient
from fastapi import status

from app.dependencies import get_link_repository
from app.schemas.link import StoredLink


TEST_URL = "https://example.com/"

def seed_link() -> str:
    code = "abc123"
    get_link_repository().create_link(
        StoredLink(
            code=code,
            url=TEST_URL,
            created_at=datetime.now(UTC),
        )
    )
    return code


def test_redirect_returns_location(client: TestClient) -> None:
    code = seed_link()

    response = client.get(f"/{code}", follow_redirects=False)

    assert response.status_code == status.HTTP_308_PERMANENT_REDIRECT
    assert response.headers["location"] == TEST_URL


def test_redirect_unknown_code_returns_404(client: TestClient) -> None:
    response = client.get("/unknown", follow_redirects=False)

    assert response.status_code == status.HTTP_404_NOT_FOUND
