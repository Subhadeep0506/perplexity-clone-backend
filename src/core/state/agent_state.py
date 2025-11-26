from typing_extensions import TypedDict


class AgentState(TypedDict):
    session_id: str
    user_id: str
    service_id: str
    api_key_id: str
    temperature: float
    max_tokens: int
    streaming: bool
    source_type: str
