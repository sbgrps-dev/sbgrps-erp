import secrets

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.db import SessionLocal
from app.routers import price_lists, products, requisitions, sites, vendors


async def require_token(request: Request) -> None:
    expected = get_settings().api_token
    if not expected:
        return
    header = request.headers.get("authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not secrets.compare_digest(token, expected):
        raise HTTPException(401, "Missing or invalid API token")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="SBGRPS ERP API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )

    api = APIRouter(prefix="/api/v1", dependencies=[Depends(require_token)])
    for module in (sites, vendors, products, requisitions, price_lists):
        api.include_router(module.router)
    app.include_router(api)

    @app.get("/healthz", tags=["ops"])
    async def healthz() -> dict[str, str]:
        async with SessionLocal() as session:
            await session.execute(text("select 1"))
        return {"status": "ok"}

    return app


app = create_app()
