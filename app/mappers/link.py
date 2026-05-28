from app.config import settings
from app.constants import MSG_LINK_CREATED, MSG_LINK_EXISTS
from app.schemas.link import LinkApiModel, ShortenResponse, StoredLink


def to_api_model(link: StoredLink) -> LinkApiModel:
    return LinkApiModel(code=link.code, url=link.url)


def to_shorten_response(link: StoredLink, *, created: bool) -> ShortenResponse:
    code = link.code
    return ShortenResponse(
        code=code,
        short_url=f"{settings.base_url.rstrip('/')}/{code}",
        original_url=str(link.url),
        message=MSG_LINK_CREATED if created else MSG_LINK_EXISTS,
    )
