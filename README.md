# Python UV Starter

This is a simple Python [uv](https://docs.astral.uv) starter in Firebase Studio.

## Running

```
uv run main.py
```

## Add dependencies

```
uv add ruff
```

## Database models and schema (core tables)

This service uses SQLAlchemy declarative models located in `src/models`.
Below are the core tables added for the Perplexity-clone application, their purpose, and the fields they store.

- **User**: Stores user account and authentication info.
	- `id` (int, PK): autoincrement primary key.
	- `username` (varchar(30), unique): unique username.
	- `full_name` (varchar(80)): user's display/full name.
	- `email` (varchar(40), unique): user's email address with format check.
	- `password` (varchar(255), nullable): password hash/storage.
	- `google_id` (varchar(50), unique, nullable): Google OAuth ID.
	- `created_at`, `updated_at` (timestamps): provided by `TimestampMixin`.

- **UserSettings**: Per-user preferences.
	- `id` (int, PK)
	- `user_id` (FK → `user.id`)
	- `language_preference` (varchar(8), nullable): e.g. `en`, default `en`.
	- `dark_mode_enabled` (boolean): default `false`.
	- `location` (varchar(100), nullable)
	- `custom_instructions` (text, nullable)
	- `created_at`, `updated_at` (timestamps)

- **Profile**: Optional user profile metadata.
	- `id` (int, PK)
	- `user_id` (FK → `user.id`)
	- `phone` (varchar(13), nullable)
	- `avatar` (text, nullable): avatar image URL or base64 string.
	- `bio` (varchar(255), nullable)
	- `created_at`, `updated_at` (timestamps)

- **Session**: Conversation sessions per-user (distinguish web/mobile).
	- `id` (int, PK)
	- `user_id` (FK → `user.id`)
	- `started_at` (date)
	- `ended_at` (date, nullable)
	- `device_type` (varchar(20), nullable): `mobile`, `web`, etc.
	- `created_at`, `updated_at` (timestamps)

- **Query**: A user's search/question inside a session. Supports follow-ups via `parent_query_id`.
	- `id` (int, PK)
	- `session_id` (FK → `session.id`)
	- `user_id` (FK → `user.id`)
	- `query_text` (text)
	- `query_type` (varchar(20), nullable): `text`, `voice`, etc.
	- `parent_query_id` (FK → `query.id`, nullable): links follow-up queries to parent.
	- `created_at`, `updated_at` (timestamps)

- **Answer**: AI-generated answer(s) for a particular query.
	- `id` (int, PK)
	- `query_id` (FK → `answer.id`)
	- `answer_text` (text)
	- `model_used` (varchar(100), nullable): model name or identifier.
	- `confidence_score` (float, nullable)
	- `created_at`, `updated_at` (timestamps)

- **Source**: Citation or reference attached to an `Answer`.
	- `id` (int, PK)
	- `answer_id` (FK → `answer.id`)
	- `source_text` (text, nullable)
	- `source_type` (varchar(50), nullable)
	- `source_url` (varchar(1024), nullable)
	- `created_at`, `updated_at` (timestamps)

- **TokenUsage**: Tracks token consumption for cost/usage analytics.
	- `id` (int, PK)
	- `user_id` (FK → `user.id`)
	- `session_id` (FK → `session.id`, nullable)
	- `query_id` (FK → `query.id`, nullable)
	- `tokens_used` (int, default 0)
	- `created_at`, `updated_at` (timestamps)

- **LoginSession**: Tracks user login sessions with JWT tokens.
	- `id` (int, PK)
	- `user_id` (FK → `user.id`)
	- `login_method` (varchar(20)): 'google', 'password', etc.
	- `is_active` (boolean, default true)
	- `device_info` (varchar(255), nullable)
	- `ip_address` (varchar(45), nullable): IPv6 support
	- `user_agent` (text, nullable)
	- `access_token` (text, nullable, indexed)
	- `refresh_token` (text, nullable)
	- `token_expires_at` (timestamp, nullable)
	- `logout_at` (timestamp, nullable)
	- `created_at`, `updated_at` (timestamps)

- **ModelMemory**: Long-term memory entries distilled from user conversations (preferences, durable facts).
	- `id` (int, PK)
	- `user_id` (FK → `user.id`)
	- `tags` (varchar(100), nullable): optional tag list or category string.
	- `title` (varchar(200)): concise human-readable summary of the memory.
	- `content` (text): detailed memory content extracted or confirmed.
	- `created_at`, `updated_at` (timestamps)

### Service catalog and per-user credentials

This project now includes an admin-managed service catalog and per-user credential storage to manage external providers (LLMs, embeddings, web search, and web scrapers).

- **ServiceCatalog**: Admin-managed catalog of available external services. Each entry represents a provider and category (for example, `llm` or `embedding`).
	- `id` (int, PK)
	- `name` (varchar(120)) — display name (e.g., "OpenAI GPT-4").
	- `slug` (varchar(80), unique) — short identifier (e.g., `openai-gpt4`).
	- `category` (varchar(30)) — `llm`, `embedding`, `web_search`, `web_scraper`, etc.
	- `provider` (varchar(60)) — provider code used by factories.
	- `default_config` (JSON, nullable) — provider defaults such as model name.
	- `is_active` (boolean) — whether the provider is enabled.

- **UserServiceCredential**: Per-user credentials that link a `User` to a `ServiceCatalog` entry.
	- `id` (int, PK)
	- `user_id` (FK → `user.id`) — `ondelete=CASCADE`
	- `service_id` (FK → `service_catalog.id`) — `ondelete=CASCADE`
	- `api_key` (text, nullable) — user-provided API key (treat as secret).
	- `config` (JSON, nullable) — optional per-user configuration overrides.
	- `is_default` (boolean) — mark a credential as the user's default for that provider.

Notes:
- Existing provider-specific model files (e.g., `api_service.py`, provider-specific `llm.py`, `embedding.py`) have been removed in favor of the catalog + credentials model. If you had keys stored in `api_service` previously, migrate them into `UserServiceCredential` rows.
- Factories (in `src/services/.../factory.py`) should use `ServiceCatalog.provider` + a `UserServiceCredential` to instantiate provider clients at runtime.

Migration suggestion:
- Add `ServiceCatalog` entries for the providers you want to support.
- Run a one-off script or Alembic migration to copy non-null API keys from any old per-provider columns (if present) into `UserServiceCredential` rows for each user.
- Remove legacy columns from the database once migration is verified.

Notes and implementation choices:
- The current implementation uses integer autoincrement primary keys (`id`) to keep changes minimal. If you prefer UUIDs for PKs (as in the original spec), I can convert the models to use UUID columns and update FKs accordingly (requires migrations).
- All models rely on `TimestampMixin` from `src/database/database.py` which sets `created_at` and `updated_at` using SQL functions.
- Relationships are implemented with SQLAlchemy `relationship()` and use `typing.TYPE_CHECKING` + forward references to avoid circular import issues.
- `parent_query_id` in `Query` forms a tree (parent/children relationship) to support follow-up queries and context-aware conversations.

Usage notes for `ModelMemory`:
- Store only high-signal, durable information (confirmed preferences, recurring facts) to reduce noise.

## Alembic Database Migrations

### Setup

Alembic is configured to work with your async PostgreSQL database and automatically detect model changes.

#### Configuration Files

- `alembic.ini` - Main Alembic configuration
- `alembic/env.py` - Migration environment setup (supports async)
- `alembic/versions/` - Migration scripts directory

### Common Commands

#### Create a New Migration

```bash
# Auto-generate migration from model changes
uv run alembic revision --autogenerate -m "description of changes"

# Create empty migration file
uv run alembic revision -m "description of changes"
```

#### Apply Migrations

```bash
# Upgrade to latest version
uv run alembic upgrade head

# Upgrade by one version
uv run alembic upgrade +1

# Upgrade to specific revision
uv run alembic upgrade <revision_id>
```

#### Rollback Migrations

```bash
# Downgrade by one version
uv run alembic downgrade -1

# Downgrade to specific revision
uv run alembic downgrade <revision_id>

# Downgrade to base (remove all migrations)
uv run alembic downgrade base
```

#### View Migration History

```bash
# Show current revision
uv run alembic current

# Show migration history
uv run alembic history

# Show migration history with details
uv run alembic history --verbose
```

### Initial Migration

The first migration adds JWT token fields to the `login_session` table:

```bash
# Apply the migration
uv run alembic upgrade head
```

This adds:
- `access_token` (TEXT, indexed)
- `refresh_token` (TEXT)
- `token_expires_at` (TIMESTAMP)

### Migration Workflow

#### 1. Modify Your Models

```python
# src/models/my_model.py
class MyModel(Base):
    # Add/modify fields
    new_field: Mapped[str] = mapped_column(String(100))
```

#### 2. Generate Migration

```bash
uv run alembic revision --autogenerate -m "add new_field to my_model"
```

#### 3. Review the Generated Migration

Check `alembic/versions/<revision>_add_new_field_to_my_model.py`:

```python
def upgrade() -> None:
    # Review the auto-generated changes
    op.add_column('my_model', sa.Column('new_field', sa.String(length=100)))

def downgrade() -> None:
    # Review the rollback changes
    op.drop_column('my_model', 'new_field')
```

#### 4. Apply Migration

```bash
uv run alembic upgrade head
```

#### 5. If Something Goes Wrong

```bash
# Rollback the last migration
uv run alembic downgrade -1

# Fix the migration file
# Then upgrade again
uv run alembic upgrade head
```

### Environment Variables

Alembic reads `DATABASE_URL` from your environment:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
```

Make sure this is set in your `.env` file.

### Production Deployment

#### Safe Deployment Process

1. **Backup the database**
   ```bash
   pg_dump dbname > backup.sql
   ```

2. **Test migration in staging**
   ```bash
   uv run alembic upgrade head
   ```

3. **Apply in production**
   ```bash
   uv run alembic upgrade head
   ```

4. **If issues occur, rollback**
   ```bash
   uv run alembic downgrade -1
   # Restore from backup if needed
   psql dbname < backup.sql
   ```

#### Automated Deployment

Add to your deployment script:

```bash
#!/bin/bash
set -e

# Load environment
source .env

# Run migrations
uv run alembic upgrade head

# Start application
uv run fastapi run
```

### CORE FLOW

#### Simple Textual Flow for Real-Time Web Search + LLM Response

1. **User Query Received**  
   User submits a question or search query.

2. **Query Reformulation & Web Search**  
   The system reformulates the query if needed and sends it simultaneously to free web search APIs (e.g., Bing Search API free tier, Google Custom Search JSON API free tier).

3. **Top Results Fetching**  
   From the search results, the system picks the top few URLs (e.g., top 5-10) and quickly fetches the full page content or main article using HTTP requests or scraping tools.

4. **Content Extraction & Cleaning**  
   Extract the main text, metadata, and relevant sections from these web pages using lightweight parsing or libraries like BeautifulSoup.

5. **LLM Prompt Construction**  
   Construct a prompt for an LLM (like OpenAI GPT-4, or open-source models running locally or on cloud) that includes the user's question plus the extracted web content as context.

6. **LLM Response Generation**  
   Send the prompt to the LLM to generate a concise, grounded answer citing facts from the web content.

7. **Post-processing & Display**  
   Filter, rank, and format the generated answer with citations and provide it as a response to the user.

***

### Free Services to Replicate This Workflow

| Workflow Step              | Suggested Free/Unpaid Service Options                                  |
|----------------------------|-----------------------------------------------------------------------|
| Web Search API             | Bing Search API free tier, Google Custom Search API free tier         |
| Web Page Fetching          | Python requests library + BeautifulSoup for HTML parsing              |
| Content Extraction         | Newspaper3k library, Readability-lxml for article text extraction     |
| LLM for Response Generation| OpenAI GPT-4/3 free trial credits, Hugging Face Inference API (free for limited use), local open-source LLMs like GPT4All or Vicuna |
| Prompt Construction & Orchestration | Custom scripting in Python or FastAPI for combining inputs/responses  |

---

# Admin

This project includes an admin dashboard for managing users, services and sessions. The admin UI uses HTMX + Tailwind and is available under `/admin` routes.

Quick start:

```bash
# Create an admin user
uv run python scripts/create_admin.py

# Start the app
uv run fastapi dev main.py
```

Open: `http://localhost:8000/admin/login`

Features:
- Admin login/logout
- Dashboard with statistics
- Service catalog CRUD (LLM, embedding, web search, web scraper)
- User management
- Session monitoring

Security notes: use HTTPS, secure cookies, JWT verification for production, and rate limiting on login routes.

For full admin setup and usage examples, see `ADMIN_README.md` and `ADMIN_SETUP.md` in the repository root.
