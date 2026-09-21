from fastapi import APIRouter

health_router = APIRouter(tags=["Health"])


@health_router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
