from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.data_store import StorageError
from app.dependencies import get_link_repository
from app.repositories.link_repo import LinkRepository
from app.mappers.link import to_api_model
from app.schemas.link import LinkApiModel, ShortenRequest, ShortenResponse
from app.services.shortener import (
    CodeGenerationError,
    DuplicateLinkError,
    create_link,
)

router = APIRouter(tags=["links"])


@router.post(
    "/shorten",
    response_model=ShortenResponse,
    responses={
        200: {
            "description": "Short link already exists for this URL",
            "model": ShortenResponse,
        },
        201: {
            "description": "Link created successfully",
            "model": ShortenResponse,
        },
        409: {"description": "Custom code already taken by another URL"},
        503: {"description": "Storage or code allocation failure"},
    },
)
async def shorten_url(
    request: ShortenRequest,
    repo: LinkRepository = Depends(get_link_repository),
) -> JSONResponse:
    try:
        result, created = create_link(request, repo)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return JSONResponse(content=result.model_dump(), status_code=status_code)
    except DuplicateLinkError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Code '{exc.code}' is already taken",
        ) from exc
    except CodeGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to allocate a unique short code",
        ) from exc
    except StorageError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message,
        ) from exc


@router.get("/links/{code}", response_model=LinkApiModel)
async def get_link_by_code(
    code: str,
    repo: LinkRepository = Depends(get_link_repository),
) -> LinkApiModel:
    try:
        link = repo.get_link(code)
    except StorageError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message,
        ) from exc
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
    try:
        return [to_api_model(link) for link in repo.list_links()]
    except StorageError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message,
        ) from exc
