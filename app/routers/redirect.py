from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from app.dependencies import get_link_repository
from app.repositories.link_repo import LinkRepository

router = APIRouter(tags=["redirect"])


@router.get("/{code}")
async def redirect_to_url(
    code: str,
    repo: LinkRepository = Depends(get_link_repository),
) -> RedirectResponse:
    link = repo.get_link(code)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )
    return RedirectResponse(url=str(link.url), status_code=status.HTTP_308_PERMANENT_REDIRECT)
