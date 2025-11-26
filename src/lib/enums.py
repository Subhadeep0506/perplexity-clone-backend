from enum import Enum


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"


class WebSearcher(Enum):
    TAVILY = "tavily"
    GOOGLE = "google"
    EXA = "exa"
    SERP = "serp"
    DUCKDUCKGO = "duckduckgo"


class WebScraper(Enum):
    SCRAPEDO = "scrapedo"
    FIRECRAWL = "firecrawl"
    CRAWL4AI = "crawl4ai"
    SCRAPER = "scraper"


class LLMProvider(Enum):
    GEMINI = "gemini"
    MISTRAL = "mistral"
    GROQ = "groq"
    COHERE = "cohere"
    NIM = "nim"
    OPENROUTER = "openrouter"
    ANTHROPIC = "anthropic"


class EmbeddingProvider(Enum):
    HUGGINGFACE_LOCAL = "huggingface_local"
    HUGGINGFACE_ENDPOINT = "huggingface_endpoint"


class CheckpointProvider(Enum):
    REDIS = "redis"
    POSTGRES = "postgres"


class MemoryProvider(Enum):
    REDIS = "redis"
    POSTGRES = "postgres"


class SourceType(Enum):
    WEB = "web"
    FILE = "file"
