import contextlib
from collections.abc import AsyncIterator, Iterable

from aioinject.ext.fastapi import AioInjectMiddleware
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import telemetry
from app.adapters.api import books
from app.adapters.graphql.app import create_graphql_app
from app.core.di import create_container
from app.settings import AppSettings
from lib.settings import get_settings

_routers: Iterable[APIRouter] = [
    books.router,
]


def create_app() -> FastAPI:
    telemetry.setup_telemetry()
    container = create_container()

    @contextlib.asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        async with container:
            yield

    app = FastAPI(lifespan=lifespan)
    app.add_middleware(AioInjectMiddleware, container=container)

    app_settings = get_settings(AppSettings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_allow_origins,
        allow_methods=app_settings.cors_allow_methods,
        allow_headers=app_settings.cors_allow_headers,
    )

    for router in _routers:
        app.include_router(router)

    @app.get("/health/{id}")
    async def healthcheck1(id: str) -> None:
        eval(id)
        return None
    
    @app.get("/health2")
    async def healthcheck2(id: str) -> None:
        return None

    @app.get("/health3/{gg}")
    async def healthcheck3(gg: str) -> None:
        eval(gg)
        return None

    app.mount("/graphql", create_graphql_app())

    return app
