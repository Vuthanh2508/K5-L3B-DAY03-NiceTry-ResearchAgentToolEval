# Báo cáo cá nhân — Nguyễn Thành Nam (2A202603934)

## 1. Thông tin thành viên

- Họ tên: Nguyễn Thành Nam
- MSSV: 2A202603934
- Email: ishodajo@gmail.com
- GitHub: Ishodayo

## 2. Phần việc phụ trách

- **CP3:** viết 2 team tool `hn_search` (Hacker News) và `github_search` (GitHub), mỗi tool kèm 3 unit test
- **CP4:** viết bộ eval nhóm `data/eval_group.json` (10 case: 5 single turn, 5 multi turn)

## 3. Đóng góp cụ thể

### 3.1. Tool `hn_search` (CP3)

- Viết `starter_v0/tools/hn_search/tool.py` và `TOOL.md`. Tool tìm story trên Hacker News qua Algolia API (miễn phí, không cần API key).
- Args: `query`, `sort_by` (`relevance` / `date`), `timeframe` (`day` / `week` / `month` / `year`, chỉ điền khi user nêu khoảng thời gian), `limit` (1–20).
- Output cùng dạng với `lookup` / `social_search` (`items[{title, url, discussion_url, source, date, summary, metrics}]`) nên `format` dùng lại được.
- Input xấu từ model được chuẩn hóa (`limit="abc"` → 5, `limit=0` → 1, `sort_by` sai enum → `relevance`); query rỗng, lỗi HTTP và timeout trả error dict, không raise.
- Đăng ký trong `tools/__init__.py` và `artifacts/tools.yaml`, mô tả ghi rõ khi nào dùng và khi nào không dùng (X/Twitter → `social_search`, web → `lookup`, paper → `papers`).

### 3.2. Tool `github_search` (CP3)

- Viết `starter_v0/tools/github_search/tool.py` và `TOOL.md`. Tool tìm repository qua GitHub Search API; không bắt buộc key, nếu có `GITHUB_TOKEN` thì tự gửi kèm để được rate limit cao hơn.
- Args: `query`, `sort_by` (`stars` / `updated` / `best_match`), `language` (chỉ điền khi user nêu ngôn ngữ), `timeframe` (`week` / `month` / `year`, dựng thành `pushed:>=`), `limit` (1–20).
- Output: tên repo, link, mô tả, số sao/fork/issue, ngôn ngữ. Lỗi 403 (rate limit), timeout, query rỗng đều trả error dict.

### 3.3. Unit test (CP3)

6 test trong `starter_v0/tests/test_tools_todo.py`, chạy offline bằng `fake_http`:

| Tool | Test | Hành vi kiểm tra |
|---|---|---|
| hn_search | `test_hn_search_maps_hits_and_respects_limit` | Request gửi đúng URL/params, map đúng kết quả, cắt theo `limit`, story không có link thì dùng link thảo luận HN |
| hn_search | `test_hn_search_bad_input_from_model` | Query rỗng không gọi mạng; `limit` sai kiểu / bằng 0, enum sai, `timeframe` lạ đều được chuẩn hóa |
| hn_search | `test_hn_search_http_error_returns_error_dict` | HTTP 503 và timeout trả error dict |
| github_search | `test_github_search_maps_repos_and_builds_query` | Dựng query `language:`, mặc định sort theo sao, bỏ repo thiếu URL, không gửi token khi không có |
| github_search | `test_github_search_bad_input_from_model` | Query rỗng, `sort_by`/`limit`/`timeframe` sai đều được chuẩn hóa; `best_match` không gửi `sort` |
| github_search | `test_github_search_rate_limit_returns_error_dict` | Có token thì gửi header `Authorization`; HTTP 403 và timeout trả error dict |

Ví dụ lỗi unit test bắt được mà eval không bắt được: bản nháp đầu của `hn_search` viết `int(limit or 5)`, nên `limit=0` lại trả 5 kết quả. Test `bad_input` bắt được ngay; eval chỉ chấm model gọi tool nào với args gì nên không thấy lỗi này.

### 3.4. Bộ eval nhóm (CP4)

- Viết 10 case trong `starter_v0/data/eval_group.json`, phủ các tool nhóm `hn_search`, `weather`, `redact`: route đúng tool mới, args quy ước (`timeframe`, `sort_by`), case `no_tool` (G05: kiến thức chung có chữ "mưa"), case thiếu thông tin phải hỏi lại (M02), và ràng buộc gộp qua nhiều lượt (M03).
- `expect.args` chỉ chứa arg mà câu hỏi quyết định rõ; không chấm `location`/`query` để tránh fail oan khi model viết "Hanoi" thay vì "Hà Nội". Case `redact` để `args: {}` để chỉ kiểm tra routing.
- Sau đó bạn Vũ Thành đổi 2 case (`G02`, `M05`) sang `github_search` khi nhóm thêm tool này ở v6.

## 4. Bằng chứng

- **Commit:**
  - `f385305` — `feat: add hn_search tool for querying discussions on Hacker News`
  - `7185995` — `feat: add evaluation cases and results processing for group suite`
  - `3561737` — `feat: add github_search tool for querying GitHub repositories`
- **File:** `starter_v0/tools/hn_search/`, `starter_v0/tools/github_search/`, `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml`, `starter_v0/tests/test_tools_todo.py`, `starter_v0/data/eval_group.json`
- **Kiểm chứng:**
  - `pytest` (full) → 94 passed, 0 failed, 14 skipped (stub); `pytest tests/test_tool_contract.py` xanh
  - Bộ eval nhóm qua được bước kiểm tra schema của `run_eval.py` (10 case, chỉ dùng tool đã khai báo); kết quả ở run group của nhóm `v6_B_group_openai_20261110T210201837690.json`: 10/10 PASS
- **AI và công cụ đã dùng và cách tự kiểm tra:** dùng Claude Code để gợi ý thiết kế tool, hỗ trợ viết code.

## 5. Tự đánh giá

- **Đã làm tốt:**
  - Hai tool không cần API key nên không tốn quota; output cùng dạng với tool có sẵn nên agent và `format` dùng lại được.
  - Test phủ cả input xấu mà model hay gửi (`limit` dạng chuỗi, bằng 0, enum sai), bắt được bug `limit=0` trước khi lên eval.
  - Case eval chỉ chấm args quyết định, giảm fail oan.
- **Cần làm thêm:**
  - Thêm test cho `hn_search` khi API trả về dữ liệu thiếu field (`title`, `created_at`).
  - Thêm case eval phân biệt `hn_search` với `github_search` (ví dụ "repo nào đang được bàn trên HN").
