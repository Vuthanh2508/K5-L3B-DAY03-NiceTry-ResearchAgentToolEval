---
name: github_search
track: core
kind: live_api
provider: GitHub REST Search API
requires_env: []
inputs: [query, sort_by, language, timeframe, limit]
outputs: [items, total_results]
side_effect: false
---
# github_search

Tìm repository trên GitHub qua https://api.github.com/search/repositories.
Không bắt buộc key (giới hạn ~10 request/phút); nếu có `GITHUB_TOKEN` trong `.env`
thì tool tự gửi kèm để được rate limit cao hơn.
Trả về `items[{title, url, source, date, summary, metrics, language}]`,
cùng shape với các tool đọc khác nên `format` dùng lại được.
Mọi lỗi (query rỗng, HTTP 403 rate limit, timeout) trả error dict, không raise.
