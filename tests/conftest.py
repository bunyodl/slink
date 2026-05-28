from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_link_repository
from app.main import app
from app.schemas.link import StoredLink
from app.services.url_normalize import url_hash

TEST_URL = "https://example.com/"


@pytest.fixture
def links_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "links.json"
    monkeypatch.setattr("app.data_store.LINKS_PATH", path)
    return path


@pytest.fixture
def client(links_file: Path) -> Generator[TestClient, None, None]:
    del links_file
    with TestClient(app) as test_client:
        yield test_client


def seed_link(
    *,
    url: str = TEST_URL,
    code: str = "abc123",
    include_url_hash: bool = True,
) -> str:
    data: dict = {
        "code": code,
        "url": url,
        "created_at": datetime.now(UTC).isoformat(),
    }
    if include_url_hash:
        data["url_hash"] = url_hash(url)

    repo = get_link_repository()
    if include_url_hash:
        repo.create_link(StoredLink.model_validate(data))
    else:
        links = {code: data}
        from app.data_store import save_links

        save_links(links)
    return code
