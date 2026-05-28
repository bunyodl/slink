from app.services.url_normalize import canonical_url, url_hash


def test_url_hash_case_insensitive() -> None:
    assert url_hash("https://x.com") == url_hash("HTTPS://X.COM")


def test_url_hash_trailing_slash() -> None:
    assert url_hash("https://example.com") == url_hash("https://example.com/")


def test_canonical_url_normalizes_scheme_and_host() -> None:
    assert canonical_url("HTTPS://EXAMPLE.COM/path") == "https://example.com/path"
