from fastapi import Request
from typing import Any


class AppState:
    def __init__(self, model: Any = None, tokenizer: Any = None, logger: Any = None):
        self.model = model
        self.tokenizer = tokenizer
        self.logger = logger


def get_app_state(request: Request) -> AppState:
    return request.app.state
