from fastapi import Request, Depends
from .app_state import get_app_state, AppState


def get_state(request: Request) -> AppState:
    return get_app_state(request)


def get_logger(state: AppState = Depends(get_state)):
    return state.logger


def get_model(state: AppState = Depends(get_state)):
    return state.model


def get_tokenizer(state: AppState = Depends(get_state)):
    return state.tokenizer
