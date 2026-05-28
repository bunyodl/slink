from datetime import UTC, datetime

import pytest

from app.dependencies import get_link_repository
from app.schemas.link import ShortenRequest, StoredLink
from app.constants import MSG_LINK_CREATED, MSG_LINK_EXISTS
from app.services.shortener import (
    CodeGenerationError,
    DuplicateLinkError,
    create_link,
)
from app.services.url_normalize import url_hash


TEST_URL = "https://example.com/"

def test_create_link_persists_to_file(links_file) -> None:
    repo = get_link_repository()
    request = ShortenRequest(url=TEST_URL)

    response, created = create_link(request, repo)

    assert created is True
    assert response.message == MSG_LINK_CREATED
    assert response.code
    assert response.short_url.endswith(f"/{response.code}")
    assert links_file.exists()
    stored = repo.get_link(response.code)
    assert stored is not None
    assert stored.url_hash == url_hash(TEST_URL)


def test_create_link_same_url_returns_existing(links_file) -> None:
    repo = get_link_repository()
    request = ShortenRequest(url=TEST_URL)

    first, first_created = create_link(request, repo)
    second, second_created = create_link(request, repo)

    assert first_created is True
    assert second_created is False
    assert second.code == first.code
    assert second.message == MSG_LINK_EXISTS


def test_create_link_same_url_different_casing(links_file) -> None:
    repo = get_link_repository()
    first, _ = create_link(ShortenRequest(url="https://example.com"), repo)
    second, created = create_link(
        ShortenRequest(url="HTTPS://EXAMPLE.COM"), repo
    )

    assert created is False
    assert second.code == first.code
    assert second.message == MSG_LINK_EXISTS


def test_find_by_url_hash_legacy_row_without_url_hash(links_file) -> None:
    from app.data_store import save_links

    repo = get_link_repository()
    save_links(
        {
            "legacy": {
                "code": "legacy",
                "url": TEST_URL,
                "created_at": datetime.now(UTC).isoformat(),
            }
        }
    )

    found = repo.find_by_url_hash(url_hash(TEST_URL))

    assert found is not None
    assert found.code == "legacy"


def test_create_link_duplicate_custom_code_raises() -> None:
    repo = get_link_repository()
    repo.create_link(
        StoredLink(
            code="dup123",
            url=TEST_URL,
            url_hash=url_hash(TEST_URL),
            created_at=datetime.now(UTC),
        )
    )
    request = ShortenRequest(url="https://other.com", custom_code="dup123")

    with pytest.raises(DuplicateLinkError):
        create_link(request, repo)


def test_create_link_collision_then_success(links_file, monkeypatch) -> None:
    repo = get_link_repository()
    repo.create_link(
        StoredLink(
            code="taken1",
            url="https://other.com",
            url_hash=url_hash("https://other.com"),
            created_at=datetime.now(UTC),
        )
    )
    codes = iter(["taken1", "free01"])

    monkeypatch.setattr(
        "app.services.shortener.generate_code",
        lambda length=None: next(codes),
    )

    response, created = create_link(ShortenRequest(url=TEST_URL), repo)

    assert created is True
    assert response.code == "free01"
    assert response.message == MSG_LINK_CREATED


def test_create_link_all_attempts_collide(links_file, monkeypatch) -> None:
    repo = get_link_repository()
    repo.create_link(
        StoredLink(
            code="taken1",
            url="https://other.com",
            url_hash=url_hash("https://other.com"),
            created_at=datetime.now(UTC),
        )
    )

    monkeypatch.setattr(
        "app.services.shortener.generate_code",
        lambda length=None: "taken1",
    )

    with pytest.raises(CodeGenerationError):
        create_link(ShortenRequest(url=TEST_URL), repo)
