from datetime import UTC, datetime

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.data_store import StorageError
from app.dependencies import get_link_repository
from app.constants import MSG_LINK_CREATED, MSG_LINK_EXISTS
from app.schemas.link import StoredLink
from app.services.url_normalize import url_hash


TEST_URL = "https://example.com/"


def seed_link() -> str:
    code = "abc123"
    get_link_repository().create_link(
        StoredLink(
            code=code,
            url=TEST_URL,
            url_hash=url_hash(TEST_URL),
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
    assert body["message"] == MSG_LINK_CREATED


def test_shorten_same_url_twice(client: TestClient) -> None:
    first = client.post("/api/shorten", json={"url": "https://example.com"})
    second = client.post("/api/shorten", json={"url": "https://example.com"})

    assert first.status_code == status.HTTP_201_CREATED
    assert first.json()["message"] == MSG_LINK_CREATED

    assert second.status_code == status.HTTP_200_OK
    assert second.json()["code"] == first.json()["code"]
    assert second.json()["message"] == MSG_LINK_EXISTS


def test_shorten_same_url_different_casing(client: TestClient) -> None:
    seed_link()

    response = client.post(
        "/api/shorten",
        json={"url": "HTTPS://EXAMPLE.COM"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == "abc123"
    assert response.json()["message"] == MSG_LINK_EXISTS


def test_shorten_trailing_slash_variant(client: TestClient) -> None:
    first = client.post("/api/shorten", json={"url": "https://example.com"})
    second = client.post("/api/shorten", json={"url": "https://example.com/"})

    assert first.status_code == status.HTTP_201_CREATED
    assert second.status_code == status.HTTP_200_OK
    assert second.json()["code"] == first.json()["code"]
    assert second.json()["message"] == MSG_LINK_EXISTS


def test_shorten_duplicate_custom_code_returns_409(client: TestClient) -> None:
    seed_link()

    response = client.post(
        "/api/shorten",
        json={"url": "https://other.com", "custom_code": "abc123"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Code 'abc123' is already taken"


def test_shorten_storage_error_returns_503(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def raise_storage_error(_links: dict) -> None:
        raise StorageError("Unable to access link storage")

    monkeypatch.setattr("app.repositories.link_repo.save_links", raise_storage_error)

    response = client.post("/api/shorten", json={"url": TEST_URL})

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


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

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
