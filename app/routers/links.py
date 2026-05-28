from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_link_repository
from app.repositories.link_repo import LinkRepository
from app.mappers.link import to_api_model
from app.schemas.link import LinkApiModel, ShortenRequest, ShortenResponse
from app.services.shortener import DuplicateLinkError, create_link

router = APIRouter(tags=["links"])


@router.post(
    "/shorten",
    response_model=ShortenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def shorten_url(
    request: ShortenRequest,
    repo: LinkRepository = Depends(get_link_repository),
) -> ShortenResponse:
    try:
        return create_link(request, repo)
    except DuplicateLinkError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Code '{exc.code}' is already taken",
        ) from exc


@router.get("/links/{code}", response_model=LinkApiModel)
async def get_link_by_code(
    code: str,
    repo: LinkRepository = Depends(get_link_repository),
) -> LinkApiModel:
    link = repo.get_link(code)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )
    return to_api_model(link)


@router.get("/links", response_model=list[LinkApiModel])
async def list_links(
    repo: LinkRepository = Depends(get_link_repository),
) -> list[LinkApiModel]:
    return [to_api_model(link) for link in repo.list_links()]
