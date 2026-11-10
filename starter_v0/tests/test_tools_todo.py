"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest
import requests

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    pytest.skip(TODO)


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    pytest.skip(TODO)


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    pytest.skip(TODO)


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    pytest.skip(TODO)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    pytest.skip(TODO)


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    pytest.skip(TODO)


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    pytest.skip(TODO)


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    pytest.skip(TODO)


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    pytest.skip(TODO)


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    pytest.skip(TODO)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    pytest.skip(TODO)


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    pytest.skip(TODO)


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    pytest.skip(TODO)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    pytest.skip(TODO)


# ---------------- redact (team tool) ----------------

def _all_strings(value):
    """Yield every string nested anywhere inside a result dict."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _all_strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _all_strings(item)


def test_redact_masks_email_phone_and_api_key() -> None:
    text = "lien he an.nguyen@company.vn, SDT 0912345678, key sk-or-v1-abc123"
    result = TOOL_FUNCTIONS["redact"](text)

    assert "error" not in result
    assert result["redaction_count"] == 3
    assert {item["type"] for item in result["findings"]} == {"email", "phone", "api_key"}

    # The whole point of the tool: no raw secret may survive anywhere in the result.
    for secret in ("an.nguyen@company.vn", "0912345678", "sk-or-v1-abc123"):
        for text_value in _all_strings(result):
            assert secret not in text_value, f"secret {secret!r} leaked into the result"


def test_redact_empty_text_returns_error_dict() -> None:
    result = TOOL_FUNCTIONS["redact"]("")

    assert result["error"] == "ValueError"
    assert "empty" in result["message"].lower()


def test_redact_invalid_extra_pattern_returns_error_dict() -> None:
    result = TOOL_FUNCTIONS["redact"]("xin chào", ["[unclosed"])

    assert result["error"] == "ValueError"
    assert "regex" in result["message"].lower()


# ---------------- weather (team tool) ----------------

def test_my_new_tool_happy_path(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test-secret")
    fake_payload = {
        "answer": "Hà Nội hôm nay trời nắng nhẹ, nhiệt độ từ 22 đến 28 độ C.",
        "results": [
            {
                "title": "Dự báo thời tiết Hà Nội",
                "url": "https://nchmf.gov.vn/hanoi-weather",
                "content": "Thời tiết Hà Nội hôm nay nhiều mây, không mưa.",
                "score": 0.95,
            }
        ]
    }
    calls = fake_http(FakeResponse(fake_payload))
    weather_tool = TOOL_FUNCTIONS["weather"]

    result = weather_tool(location="Hà Nội", timeframe="today")

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.tavily.com/search"
    assert calls[0]["headers"]["Authorization"] == "Bearer tvly-test-secret"
    assert "Hà Nội" in calls[0]["json"]["query"]
    assert calls[0]["json"]["include_answer"] is True
    assert result["tool"] == "weather"
    assert result["location"] == "Hà Nội"
    assert result["timeframe"] == "today"
    assert "Hà Nội hôm nay trời nắng nhẹ" in result["summary"]
    assert len(result["items"]) == 1
    assert result["items"][0]["source"] == "nchmf.gov.vn"


def test_my_new_tool_bad_input_from_model(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test-secret")
    calls = fake_http(FakeResponse({"results": []}))
    weather_tool = TOOL_FUNCTIONS["weather"]

    result_empty = weather_tool(location="   ")
    assert result_empty["tool"] == "weather"
    assert result_empty["error"] == "ValueError"
    assert "Location cannot be empty" in result_empty["message"]
    assert len(calls) == 0


def test_my_new_tool_failure_returns_error_dict(monkeypatch) -> None:
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    weather_tool = TOOL_FUNCTIONS["weather"]

    result = weather_tool(location="Đà Nẵng")
    assert isinstance(result, dict)
    assert result["tool"] == "weather"
    assert result["error"] == "RuntimeError"
    assert "Missing TAVILY_API_KEY" in result["message"]


# ---------------- hn_search ----------------

def test_hn_search_maps_hits_and_respects_limit(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": [
        {"objectID": "1", "title": "Show HN: Agent eval", "url": "https://www.example.com/a", "points": 120, "num_comments": 45, "created_at": "2026-11-01T00:00:00Z"},
        {"objectID": "2", "title": "Ask HN: no link", "url": None, "points": 10, "num_comments": 3},
        {"objectID": "3", "title": "Third", "url": "https://x.org/c"},
    ]}))
    result = TOOL_FUNCTIONS["hn_search"](query="AI agent eval", limit=2)
    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search"
    assert calls[0]["params"]["query"] == "AI agent eval"
    assert calls[0]["params"]["hitsPerPage"] == 2
    assert len(result["items"]) == 2
    first, second = result["items"]
    assert first["source"] == "example.com"
    assert first["metrics"] == {"points": 120, "comments": 45}
    assert second["url"] == "https://news.ycombinator.com/item?id=2"


def test_hn_search_bad_input_from_model(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))
    empty = TOOL_FUNCTIONS["hn_search"](query="   ")
    assert empty["error"] == "ValueError" and calls == []
    result = TOOL_FUNCTIONS["hn_search"](query="LLM", sort_by="newest", limit="abc", timeframe="decade")
    assert "error" not in result
    assert result["sort_by"] == "relevance"
    assert calls[0]["params"]["hitsPerPage"] == 5
    assert "numericFilters" not in calls[0]["params"]
    TOOL_FUNCTIONS["hn_search"](query="LLM", sort_by="date", limit=0, timeframe="week")
    assert calls[1]["url"].endswith("/search_by_date")
    assert calls[1]["params"]["hitsPerPage"] == 1
    assert calls[1]["params"]["numericFilters"].startswith("created_at_i>")


def test_hn_search_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))
    result = TOOL_FUNCTIONS["hn_search"](query="OpenAI")
    assert result["tool"] == "hn_search"
    assert result["error"] == "HTTPError"
    fake_http(requests.Timeout("timed out"))
    assert TOOL_FUNCTIONS["hn_search"](query="OpenAI")["error"] == "Timeout"


# ---------------- github_search ----------------

def test_github_search_maps_repos_and_builds_query(monkeypatch, fake_http) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    calls = fake_http(FakeResponse({"total_count": 2, "items": [
        {"full_name": "org/agent-eval", "html_url": "https://github.com/org/agent-eval", "description": "Eval for agents",
         "stargazers_count": 1200, "forks_count": 80, "open_issues_count": 5, "language": "Python", "pushed_at": "2026-11-01T00:00:00Z"},
        {"full_name": "no/url"},
    ]}))
    result = TOOL_FUNCTIONS["github_search"](query="agent evaluation", language="Python", limit=3)
    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"]["q"] == "agent evaluation language:Python"
    assert calls[0]["params"]["sort"] == "stars"
    assert calls[0]["params"]["per_page"] == 3
    assert "Authorization" not in calls[0]["headers"]
    assert len(result["items"]) == 1
    item = result["items"][0]
    assert item["title"] == "org/agent-eval"
    assert item["metrics"]["stars"] == 1200


def test_github_search_bad_input_from_model(monkeypatch, fake_http) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    calls = fake_http(FakeResponse({"items": []}))
    empty = TOOL_FUNCTIONS["github_search"](query="")
    assert empty["error"] == "ValueError" and calls == []
    result = TOOL_FUNCTIONS["github_search"](query="rag", sort_by="popular", limit="abc", timeframe="decade")
    assert "error" not in result
    assert result["sort_by"] == "stars"
    assert calls[0]["params"]["per_page"] == 5
    assert "pushed:" not in calls[0]["params"]["q"]
    TOOL_FUNCTIONS["github_search"](query="rag", sort_by="best_match", limit=0, timeframe="month")
    assert calls[1]["params"]["per_page"] == 1
    assert "sort" not in calls[1]["params"]
    assert "pushed:>=" in calls[1]["params"]["q"]


def test_github_search_rate_limit_returns_error_dict(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    calls = fake_http(FakeResponse(status_code=403))
    result = TOOL_FUNCTIONS["github_search"](query="llm")
    assert calls[0]["headers"]["Authorization"] == "Bearer test-token"
    assert result["tool"] == "github_search"
    assert result["error"] == "HTTPError"
    fake_http(requests.Timeout("timed out"))
    assert TOOL_FUNCTIONS["github_search"](query="llm")["error"] == "Timeout"
