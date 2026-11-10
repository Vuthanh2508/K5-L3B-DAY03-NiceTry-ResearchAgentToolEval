from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any

import requests

from tools._shared import TIMEOUT, err

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
TIMEFRAME_DAYS = {"week": 7, "month": 30, "year": 365}


def github_search(query: str = "", sort_by: str = "stars", language: str = "", timeframe: str | None = None, limit: int = 5) -> dict[str, Any]:
    """Tìm repository trên GitHub (Search API, không bắt buộc key)."""
    try:
        query = " ".join(str(query or "").split())
        if not query:
            return {"tool": "github_search", "error": "ValueError", "message": "query must not be empty", "items": []}
        try:
            limit = max(1, min(int(5 if limit is None else limit), 20))  # model hay gửi "5", 0, -1
        except (TypeError, ValueError):
            limit = 5
        sort_by = sort_by if sort_by in {"stars", "updated", "best_match"} else "stars"

        q = query
        language = " ".join(str(language or "").split())
        if language:
            q += f" language:{language}"
        if timeframe in TIMEFRAME_DAYS:
            q += f" pushed:>={(date.today() - timedelta(days=TIMEFRAME_DAYS[timeframe])).isoformat()}"

        params: dict[str, Any] = {"q": q, "per_page": limit}
        if sort_by != "best_match":
            params["sort"] = sort_by
            params["order"] = "desc"
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "AI20k-Day03-Research-Agent"}
        token = os.getenv("GITHUB_TOKEN")  # tùy chọn: có token thì rate limit cao hơn
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = requests.get(GITHUB_SEARCH_URL, params=params, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        items = []
        for repo in data.get("items", [])[:limit]:
            if not repo.get("html_url"):
                continue
            items.append({
                "title": repo.get("full_name") or "",
                "url": repo["html_url"],
                "source": "github.com",
                "date": repo.get("pushed_at"),
                "summary": (repo.get("description") or "")[:280],
                "metrics": {
                    "stars": repo.get("stargazers_count"),
                    "forks": repo.get("forks_count"),
                    "open_issues": repo.get("open_issues_count"),
                },
                "language": repo.get("language"),
            })
        return {"tool": "github_search", "query": query, "api_query": q, "sort_by": sort_by,
                "total_results": data.get("total_count"), "items": items}
    except Exception as exc:
        return err("github_search", exc)
