import secrets
import string
from datetime import UTC, datetime

from app.config import settings
from app.mappers.link import to_shorten_response
from app.repositories.link_repo import LinkRepository
from app.schemas.link import ShortenRequest, ShortenResponse, StoredLink
from app.services.url_normalize import url_hash


class DuplicateLinkError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Link with code '{code}' already exists")


class CodeGenerationError(Exception):
    pass


def generate_code(length: int | None = None) -> str:
    size = length or settings.short_code_length
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(size))


def create_link(
    request: ShortenRequest, repo: LinkRepository
) -> tuple[ShortenResponse, bool]:
    target_hash = url_hash(request.url)

    existing = repo.find_by_url_hash(target_hash)
    if existing:
        return to_shorten_response(existing, created=False), False

    if request.custom_code is not None:
        code = request.custom_code
        if repo.link_exists(code):
            occupied = repo.get_link(code)
            if occupied is not None and url_hash(occupied.url) == target_hash:
                return to_shorten_response(occupied, created=False), False
            raise DuplicateLinkError(code)

        link = StoredLink(
            code=code,
            url=request.url,
            url_hash=target_hash,
            created_at=datetime.now(UTC),
        )
        repo.create_link(link)
        return to_shorten_response(link, created=True), True

    for _ in range(settings.max_code_generation_attempts):
        code = generate_code()
        if not repo.link_exists(code):
            break
        occupied = repo.get_link(code)
        if occupied is not None and url_hash(occupied.url) == target_hash:
            return to_shorten_response(occupied, created=False), False
    else:
        raise CodeGenerationError()

    link = StoredLink(
        code=code,
        url=request.url,
        url_hash=target_hash,
        created_at=datetime.now(UTC),
    )
    repo.create_link(link)
    return to_shorten_response(link, created=True), True
