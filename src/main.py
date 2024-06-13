import json
import logging
import secrets
from pathlib import Path
from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from core.configuration import settings
from core.database.initiator import init_models
from core.redis.client import pool, get_redis_client

from app.routers import api_router


logger = settings.LOGGER
current_file_path = Path(__file__).resolve()
locales_path = current_file_path.parent / "locales"
docs_development_security = HTTPBasic()
openapi_tags = json.loads(open(f"{locales_path}/tags_metadata.json", "r").read())


@asynccontextmanager
async def lifespan(app: FastAPI):    
    await init_models(drop_all=settings.DROP_TABLES)
    
    async with get_redis_client() as client:
        logger.info(f"Redis ping returned with: {await client.ping()}.")

    yield

    await pool.aclose()


app = FastAPI(
    openapi_tags=openapi_tags,
    openapi_url="/openapi.json" if settings.ENVIRONMENT == "local" else None,
    docs_url="/docs" if settings.ENVIRONMENT == "local" else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.include_router(api_router)


if settings.ENVIRONMENT == "local":
    @app.get("/")
    async def root_redirect():
        return RedirectResponse("/docs")
    

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def __basic_admin_auth(
    credentials: Annotated[HTTPBasicCredentials, Depends(docs_development_security)]
):
    current_username_bytes = credentials.username.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, b"admin"
    )
    current_password_bytes = credentials.password.encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, b"admin"
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
        
    return credentials.username


@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation(_: str = Depends(__basic_admin_auth)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/openapi.json", include_in_schema=False)
async def openapi(_: str = Depends(__basic_admin_auth)):
    return get_openapi(routes=app.routes, tags=openapi_tags)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="main:app",
        host=settings.DOMAIN,
        port=8000,
        reload=settings.ENVIRONMENT == "local",
        proxy_headers=not settings.ENVIRONMENT == "local",
    )
