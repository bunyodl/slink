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


def test_shorten_valid_url(client: TestClient) -> None:
    response = client.post(
        "/api/shorten",
        json={"url": TEST_URL},
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["code"]
    assert body["short_url"].endswith(f"/{body['code']}")
    assert body["original_url"] == TEST_URL


def test_shorten_duplicate_custom_code_returns_409(client: TestClient) -> None:
    seed_link()

    response = client.post(
        "/api/shorten",
        json={"url": TEST_URL, "custom_code": "abc123"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_get_link_by_code(client: TestClient) -> None:
    code = seed_link()

    response = client.get(f"/api/links/{code}")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body == {"code": code, "url": TEST_URL}
    assert "created_at" not in body


def test_get_link_unknown_code_returns_404(client: TestClient) -> None:
    response = client.get("/api/links/missing")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_links(client: TestClient) -> None:
    seed_link()

    response = client.get("/api/links")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body) == 1
    assert set(body[0].keys()) == {"code", "url"}


def test_shorten_invalid_url_returns_422(client: TestClient) -> None:
    response = client.post("/api/shorten", json={"url": "not-a-url"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
