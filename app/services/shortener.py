import secrets
import string
from datetime import UTC, datetime

from app.config import settings
from app.repositories.link_repo import LinkRepository
from app.schemas.link import ShortenRequest, ShortenResponse, StoredLink


class DuplicateLinkError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Link with code '{code}' already exists")


def generate_code(length: int | None = None) -> str:
    size = length or settings.short_code_length
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(size))


def create_link(request: ShortenRequest, repo: LinkRepository) -> ShortenResponse:
    code = request.custom_code or generate_code()
    if repo.link_exists(code):
        raise DuplicateLinkError(code)

    link = StoredLink(
        code=code,
        url=request.url,
        created_at=datetime.now(UTC),
    )
    repo.create_link(link)

    original_url = str(request.url)
    return ShortenResponse(
        code=code,
        short_url=f"{settings.base_url.rstrip('/')}/{code}",
        original_url=original_url,
    )
