# Slink

Local URL shortener built with FastAPI. Links are stored in `data/links.json` (git-ignored).

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload
```

- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/shorten` | Create short link |
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

## Storage

Saved links live in `data/links.json`. The file is created on first save and is not committed (see `.gitignore`).

## Tests

```bash
pytest
```
