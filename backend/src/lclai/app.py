"""lclAI FastAPI 应用入口。"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.types import Scope

from lclai.config import AppSettings, get_settings
from lclai.model_gateway import describe_model_providers
from lclai.providers import ProviderDescriptor, ProviderKind, ProviderRegistry
from lclai.storage import LocalStorage


class SPAStaticFiles(StaticFiles):
    """为无扩展名的前端路由回退到 index.html。"""

    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            response = await super().get_response(path, scope)
        except HTTPException as error:
            if error.status_code == 404 and not Path(path).suffix:
                return await super().get_response("index.html", scope)
            raise
        if response.status_code == 404 and not Path(path).suffix:
            return await super().get_response("index.html", scope)
        return response


def _default_provider_registry(settings: AppSettings) -> ProviderRegistry:
    return ProviderRegistry(
        [
            ProviderDescriptor(
                provider_id="openai",
                kind=ProviderKind.MODEL,
                display_name="OpenAI",
                configured=(
                    settings.openai_api_key is not None
                    and bool(settings.openai_model_id)
                ),
                diagnostic="基础阶段不执行真实模型健康调用",
            ),
            ProviderDescriptor(
                provider_id="ark",
                kind=ProviderKind.MODEL,
                display_name="火山方舟",
                configured=(
                    settings.ark_api_key is not None and bool(settings.ark_model_id)
                ),
                diagnostic="基础阶段不执行真实模型健康调用",
            ),
            ProviderDescriptor(
                provider_id="market-data",
                kind=ProviderKind.MARKET_DATA,
                display_name="行情数据",
                diagnostic="尚未配置行情 Provider",
            ),
            ProviderDescriptor(
                provider_id="news",
                kind=ProviderKind.NEWS,
                display_name="新闻与舆情",
                diagnostic="尚未配置新闻 Provider",
            ),
            ProviderDescriptor(
                provider_id="vector-store",
                kind=ProviderKind.VECTOR_STORE,
                display_name="本地向量存储",
                diagnostic="尚未实现 RAG 存储",
            ),
            ProviderDescriptor(
                provider_id="qmt",
                kind=ProviderKind.TRADING,
                display_name="QMT 交易",
                diagnostic="尚未配置 QMT，不会发送真实订单",
            ),
        ]
    )


def create_app(
    *,
    settings: AppSettings | None = None,
    storage: LocalStorage | None = None,
    provider_registry: ProviderRegistry | None = None,
    frontend_dist: Path | None = None,
) -> FastAPI:
    """创建可注入本地依赖的应用实例。"""

    resolved_settings = settings or get_settings()
    resolved_storage = storage or LocalStorage(resolved_settings.data_dir)
    resolved_providers = provider_registry or _default_provider_registry(
        resolved_settings
    )

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.storage_readiness = resolved_storage.initialize()
        yield

    application = FastAPI(title="lclAI", version="0.1.0", lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["Accept", "Content-Type"],
    )

    @application.get("/api/v1/health/live")
    def live() -> dict[str, str]:
        return {"status": "alive"}

    @application.get("/api/v1/health/ready")
    def ready() -> JSONResponse:
        storage_readiness = application.state.storage_readiness
        is_ready = storage_readiness.ready
        payload = {
            "status": "ready" if is_ready else "not_ready",
            "core": {
                "configuration": "ready",
                "storage": "ready" if is_ready else "not_ready",
            },
            "safe_mode": "local_only",
            "detail": (
                "核心本地服务已就绪"
                if is_ready
                else f"{storage_readiness.code}: {storage_readiness.detail}"
            ),
        }
        return JSONResponse(payload, status_code=200 if is_ready else 503)

    @application.get("/api/v1/providers")
    def providers() -> dict[str, object]:
        return {
            "providers": [
                provider.model_dump(mode="json")
                for provider in resolved_providers.list()
            ]
        }

    @application.get("/api/v1/settings/providers")
    def provider_settings() -> dict[str, object]:
        return {
            "providers": [
                description.model_dump(mode="json")
                for description in describe_model_providers(resolved_settings)
            ]
        }

    resolved_frontend_dist = frontend_dist or (
        Path(__file__).resolve().parents[3] / "frontend" / "dist"
    )
    if (resolved_frontend_dist / "index.html").is_file():
        application.mount(
            "/",
            SPAStaticFiles(directory=resolved_frontend_dist, html=True),
            name="frontend",
        )

    return application


app = create_app()
