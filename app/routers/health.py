from fastapi import APIRouter

router = APIRouter(tags=["health"])

# Python's dict[str, str] is like
# Record<string, string> in TypeScript

@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
