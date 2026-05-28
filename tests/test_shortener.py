from datetime import UTC, datetime

import pytest

from app.dependencies import get_link_repository
from app.schemas.link import ShortenRequest, StoredLink
from app.services.shortener import DuplicateLinkError, create_link


TEST_URL = "https://example.com/"

def test_create_link_persists_to_file(links_file) -> None:
    repo = get_link_repository()
    request = ShortenRequest(url=TEST_URL)

    response = create_link(request, repo)

    assert response.code
    assert response.short_url.endswith(f"/{response.code}")
    assert links_file.exists()
    assert repo.get_link(response.code) is not None


def test_create_link_duplicate_custom_code_raises() -> None:
    repo = get_link_repository()
    repo.create_link(
        StoredLink(
            code="dup123",
            url=TEST_URL,
            created_at=datetime.now(UTC),
        )
    )
    request = ShortenRequest(url="https://other.com", custom_code="dup123")

    with pytest.raises(DuplicateLinkError):
        create_link(request, repo)
