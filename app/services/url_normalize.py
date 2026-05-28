import hashlib

from pydantic import HttpUrl


def canonical_url(url: str | HttpUrl) -> str:
    """Normalize scheme/host casing, trailing slashes, etc. via Pydantic."""
    return str(HttpUrl(url))


def url_hash(url: str | HttpUrl) -> str:
    canonical = canonical_url(url)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
