# Adding Search Engines

This guide is the single workflow for adding a new DDGS backend.

## 1. Choose the category and result shape

Pick one of the supported categories:

- `text` -> `TextResult`
- `images` -> `ImagesResult`
- `videos` -> `VideosResult`
- `news` -> `NewsResult`
- `books` -> `BooksResult`

The category is used by `DDGS().text()`, `DDGS().videos()`, etc., and by auto-discovery.

## 2. Create the engine module

Add a new file under `ddgs/engines/`, for example:

- `ddgs/engines/example_videos.py`

Implement a subclass of `BaseSearchEngine` with these class attributes:

- `name`: backend key exposed to users (for example `youtube`)
- `category`: one of `text/images/videos/news/books`
- `provider`: upstream provider identity used for provider de-duplication
- `search_url` and `search_method`

You must implement:

- `build_payload(...) -> dict[str, Any]`

You can optionally override:

- `extract_results(...)` for JSON/custom payloads
- `post_extract_results(...)` for normalization/sanitization

Template:

```python
from typing import Any

from ddgs.base import BaseSearchEngine
from ddgs.results import VideosResult


class ExampleVideos(BaseSearchEngine[VideosResult]):
    name = "example"
    category = "videos"
    provider = "example"
    search_url = "https://example.com/search"
    search_method = "GET"

    def build_payload(
        self,
        query: str,
        region: str,
        safesearch: str,
        timelimit: str | None,
        page: int = 1,
        **kwargs: str,
    ) -> dict[str, Any]:
        return {"q": query}
```

## 3. Understand discovery and registration

No manual engine registry edit is needed.

`ddgs/engines/__init__.py` auto-discovers every class that:

- subclasses `BaseSearchEngine`
- is not named with a `Base*` prefix
- has `disabled != True`
- defines valid string `name` and `category`

If those conditions are met, your backend is available to `DDGS` automatically.

## 4. Update CLI choices manually

CLI backend options are explicit and must be updated:

- `ddgs/cli.py`

Add your backend key to the relevant command `click.Choice(...)`.

## 5. Update docs manually

Update backend-facing docs:

- `README.md` engines table
- category-specific examples if needed
- API examples if backend behavior matters for API users

## 6. Add tests

Minimum expected coverage:

- parser/unit test for extraction logic from representative payload
- integration smoke test that validates result structure
- CLI smoke path (if backend is exposed in CLI choices)

Network-heavy tests are useful but should be paired with deterministic parser tests.

## 7. Troubleshooting

- Provider dedupe:
  `DDGS` keeps one engine per `provider` in a single search run. Use a unique provider if you need independent aggregation.
- Parsing drift:
  Keep extraction isolated in helper functions so site changes are localized.
- Empty results:
  Return `[]` for parse failures; let the aggregator continue with other engines.
- Timeout behavior:
  Reuse base HTTP client/request flow so timeout and proxy handling stay consistent.
