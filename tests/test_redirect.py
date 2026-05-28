from fastapi.testclient import TestClient
from fastapi import status

from tests.conftest import TEST_URL, seed_link


def test_redirect_returns_location(client: TestClient) -> None:
    code = seed_link()

    response = client.get(f"/{code}", follow_redirects=False)

    assert response.status_code == status.HTTP_308_PERMANENT_REDIRECT
    assert response.headers["location"] == TEST_URL


def test_redirect_unknown_code_returns_404(client: TestClient) -> None:
    response = client.get("/unknown", follow_redirects=False)

    assert response.status_code == status.HTTP_404_NOT_FOUND
