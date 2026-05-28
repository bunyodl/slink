from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


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
