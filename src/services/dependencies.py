from fastapi import Request, Depends
from .app_state import get_app_state, AppState
from src.core.settings import Settings
from src.core.container import ServiceContainer
from src.core.registry import AdapterRegistry


def get_state(request: Request) -> AppState:
    return get_app_state(request)


def get_logger(state: AppState = Depends(get_state)):
    return state.logger


def get_model(state: AppState = Depends(get_state)):
    return state.model


def get_tokenizer(state: AppState = Depends(get_state)):
    return state.tokenizer


# New DI functions for settings and adapters
def get_settings_dep(request: Request) -> Settings:
    """Get settings from app state."""
    return request.app.state.settings


def get_container_dep(request: Request) -> ServiceContainer:
    """Get service container from app state."""
    return request.app.state.container


def get_registry_dep(request: Request) -> AdapterRegistry:
    """Get adapter registry from app state."""
    return request.app.state.registry


def get_llm(container: ServiceContainer = Depends(get_container_dep)):
    """Get LLM adapter."""
    return container.get_llm()


def get_embeddings(container: ServiceContainer = Depends(get_container_dep)):
    """Get embeddings adapter."""
    return container.get_embeddings()


def get_vector_store(container: ServiceContainer = Depends(get_container_dep)):
    """Get vector store adapter."""
    return container.get_vector_store()


def get_web_search(container: ServiceContainer = Depends(get_container_dep)):
    """Get web search adapter."""
    return container.get_web_search()


def get_web_scraper(container: ServiceContainer = Depends(get_container_dep)):
    """Get web scraper adapter."""
    return container.get_web_scraper()


def get_storage(container: ServiceContainer = Depends(get_container_dep)):
    """Get storage adapter."""
    return container.get_storage()


def get_memory(container: ServiceContainer = Depends(get_container_dep)):
    """Get memory store."""
    return container.get_memory()


def get_checkpointer(container: ServiceContainer = Depends(get_container_dep)):
    """Get checkpointer."""
    return container.get_checkpointer()
