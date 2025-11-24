FROM python:3.13-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY . /app
RUN sudo apt-get update && sudo apt-get install -y build-essential && \
    sudo rm -rf /var/lib/apt/lists/*
RUN uv install --no-cache-dir --no-dev
RUN crawl4ai-setup
EXPOSE 8089
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8089"]