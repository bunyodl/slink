# Slink

Slink is a lightweight URL shortener API built with FastAPI. Create short links with optional custom codes, deduplicate by canonical URL, list and resolve links, and redirect via permanent 308 responses. Persists to local JSON for simple self-hosted use.

Links are stored in `data/links.json` (git-ignored).

## Frontend

A web UI is not implemented yet. Use the REST API (see [Endpoints](#endpoints)) or Swagger at `/docs` when the server is running.

## Setup

From the repo root (Git Bash on Windows):

```bash
./scripts/setup.sh
```

Creates `.venv`, installs dependencies from `requirements.txt`, and copies `.env.example` to `.env` if `.env` does not exist yet.

## Run

```bash
./scripts/dev.sh
```

Starts the API with reload at http://127.0.0.1:8000 (see `BASE_URL` in `.env`).

- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/shorten` | Create or reuse short link (**201** new, **200** existing URL) |
| GET | `/api/links/{code}` | Link metadata |
| GET | `/api/links` | List all links |
| GET | `/{code}` | **308** permanent redirect to original URL |

## Examples

```bash
curl -X POST http://127.0.0.1:8000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

curl http://127.0.0.1:8000/api/links/abc123
curl -I http://127.0.0.1:8000/abc123
```

### POST `/api/shorten` response

| Field | Description |
|-------|-------------|
| `code` | Short code |
| `short_url` | Full short URL (`BASE_URL` + code) |
| `original_url` | Stored destination URL |
| `message` | `"Link created successfully"` (**201**) or `"Short link already exists for this URL"` (**200**) |

Submitting the same URL again (after canonicalization — scheme/host casing and trailing slashes) returns **200** with the existing code and the reuse message. A new URL returns **201**.

Full decision flow (dedup, custom codes, collisions): [docs/post-shorten-flow.md](docs/post-shorten-flow.md).

## Storage

Saved links live in `data/links.json`. Each entry includes `code`, `url`, `url_hash` (SHA-256 of the canonical URL for deduplication), and `created_at`. The file is created on first save and is not committed (see `.gitignore`).

## Tests

```bash
pytest
```
