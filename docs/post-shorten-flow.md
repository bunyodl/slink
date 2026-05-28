# POST `/api/shorten` decision flow

How `create_link` in [`app/services/shortener.py`](../app/services/shortener.py) chooses a response. URLs are deduplicated via a canonical form and SHA-256 `url_hash` (see [`app/services/url_normalize.py`](../app/services/url_normalize.py)).

## Flow

```mermaid
flowchart TD
  req[POST /api/shorten] --> canon[Canonicalize URL]
  canon --> hash[Compute url_hash]
  hash --> byHash{url_hash in DB?}
  byHash -->|yes| ret200["200 + existing message"]
  byHash -->|no| custom{custom_code set?}
  custom -->|yes| custCheck{code taken?}
  custCheck -->|no| save["Persist url + url_hash + 201"]
  custCheck -->|yes same hash| ret200
  custCheck -->|yes other hash| err409[409 Conflict]
  custom -->|no| loop[Generate code]
  loop --> coll{code exists?}
  coll -->|no| save
  coll -->|yes same hash| ret200
  coll -->|yes other hash| loop
  loop --> max{max attempts?}
  max -->|yes| err503[503]
```

## HTTP outcomes

| Situation | HTTP | `message` (success body) |
| --------- | ---- | ------------------------ |
| New link | **201** | `"Link created successfully"` |
| URL already shortened (hash match) | **200** | `"Short link already exists for this URL"` |
| Custom code taken by another URL | **409** | `detail`: `"Code '{code}' is already taken"` |
| Storage I/O or corrupt JSON | **503** | Storage error message from [`app/data_store.py`](../app/data_store.py) |
| Auto code: all attempts collide with other URLs | **503** | `"Unable to allocate a unique short code"` |

Same URL with different scheme/host casing or trailing slash resolves to the same `url_hash` and returns **200** with the existing code.
