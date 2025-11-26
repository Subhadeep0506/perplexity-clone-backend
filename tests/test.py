import os, sys

cwd = os.getcwd()
project_root = cwd
if os.path.basename(cwd) == "tests":
    project_root = os.path.dirname(cwd)
elif os.path.exists(os.path.join(cwd, "src")):
    project_root = cwd
else:
    curr = cwd
    while curr and curr != os.path.dirname(curr):
        if os.path.exists(os.path.join(curr, "src")):
            project_root = curr
            break
        curr = os.path.dirname(curr)
sys.path.append(project_root)

from dotenv import load_dotenv

_ = load_dotenv(os.path.join(project_root, ".env"))

from src.services.llm.factory import create_llm
from src.services.web_scraper.factory import create_scraper
from src.services.web_search.factory import create_web_search
from src.services.memory.factory import create_memory, create_checkpointer
from src.services.vector_store.factory import create_vector_store
from src.services.embedding.factory import create_embeddings
from src.lib.enums import *

llm = create_llm(
    provider=LLMProvider.COHERE.value,
    model="command-a-03-2025", #"command-a-reasoning-08-2025",
    api_key=os.getenv("COHERE_API_KEY"),
)
searcher = create_web_search(
    provider=WebSearcher.GOOGLE.value,
)
scraper = create_scraper(
    provider=WebScraper.CRAWL4AI.value,
)
embeddding = create_embeddings(
    provider=EmbeddingProvider.HUGGINGFACE_ENDPOINT.value,
    api_key=os.getenv("HF_API_KEY"),
)
vectorstore = create_vector_store(embeddings=embeddding)

# store = create_memory(
#     provider=MemoryProvider.POSTGRES.value, conn_string=os.getenv("MEMORY_DATABASE_URL")
# )
# checkpointer = create_checkpointer(
#     provider=MemoryProvider.REDIS.value,
# )

async def main():
    # urls = await searcher.arun("What are the new features of langchain v1?")
    # scrapes = await scraper.aload(urls=[res["url"] for res in urls[:3]])

    # print("Search Results:", scrapes)
    respo = llm.stream("Explain the theory of relativity in simple terms.")
    for chunk in respo:
        print(chunk.content, end="", flush=True)


import asyncio

asyncio.run(main())

# from langchain_cohere import ChatCohere
# import os
# from dotenv import load_dotenv

# _ = load_dotenv(".env")

# llm = ChatCohere(
#     model="command-a-reasoning-08-2025",
#     api_key=os.getenv("COHERE_API_KEY"),
# )
# resp = llm.invoke("Explain the theory of relativity in simple terms.")
# print(resp)
