from langchain_cohere import ChatCohere
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os

cohere_model = ChatCohere(
    model="command-a-03-2025",
    cohere_api_key="",
    temperature=0.7,
    max_tokens=1024,
    streaming=False,
)

nim_model = ChatOpenAI(
    model="qwen/qwen3-next-80b-a3b-thinking",
    api_key="nvapi-",
    base_url="https://integrate.api.nvidia.com/v1",
    temperature=0.7,
    max_tokens=1024,
    streaming=False,
)

mistral_model = ChatMistralAI(
    model="mistral-medium-2508",
    mistral_api_key="",
    temperature=0.7,
    max_tokens=1024,
    streaming=False,
)

groq_model = ChatGroq(
    model="qwen/qwen3-32b",
    api_key="",
    temperature=0.7,
    max_tokens=1024,
    streaming=False,
)

gemini_model = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key="",
    temperature=0.7,
    max_tokens=1024,
    streaming=False,
)

openrouter_model = ChatOpenAI(
    model="openai/gpt-oss-20b",
    api_key="",
    base_url="https://openrouter.ai/api/v1",
    temperature=0.7,
    max_tokens=1024,
    streaming=False,
)

claude_model = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    anthropic_api_key="",
    temperature=0.7,
    max_tokens=1024,
    streaming=False,
)

print(model.invoke("Hi, can you answer meddical queries?"))
