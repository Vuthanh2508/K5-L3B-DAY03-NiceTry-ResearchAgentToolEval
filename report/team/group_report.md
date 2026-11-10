# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần:
> - **Phần A (mục 2)**: giới thiệu agent, ngắn gọn.
> - **Phần B (mục 3–8)**: chi tiết và bằng chứng, lấy từ run JSON, version_log, transcript và commit.
>
> Mỗi số liệu trỏ tới file thật trong repo. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: NiceTry
- Lớp: L3B
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model: OpenAI `gpt-4o-mini` cho toàn bộ run v0–v6 có số liệu trong báo cáo. Một run OpenRouter (`v0_B_base_openrouter_…`) được giữ làm tham khảo, không dùng để so sánh
- Commit chốt: c5431a7

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent ,agent tìm tin tức và bài đăng X theo từ khóa hoặc theo tài khoản, đọc nội dung một URL, tra cứu thời tiết, tìm thảo luận trên Hacker News và repo trên GitHub, và che thông tin nhạy cảm trước khi chia sẻ. Khi thiếu thông tin (tên tài khoản, URL, địa điểm), agent hỏi lại bằng `clarify` thay vì đoán. Trước khi gửi nội dung lên Telegram, agent phải hỏi xác nhận.

**Cách chạy UI** (từ thư mục `starter_v0`):

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501
```

Dependency `streamlit` đã có trong `starter_v0/requirements.txt`. Mở `http://localhost:8501`. Sidebar mặc định provider `openai`, nhãn `v6`.

**Link dùng thử:** `https://thesaurus-italiano-households-lie.trycloudflare.com`

### A2. Tool agent có

Tổng cộng 14 tool được khai báo trong [tools.yaml](../../starter_v0/artifacts/tools.yaml). 10 tool là của starter, 4 tool do nhóm thêm.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin (text, yes/no hoặc chọn) | không |
| timeline | Lấy bài đăng gần đây của một tài khoản X | không |
| social_search | Tìm bài đăng X theo từ khóa (Latest/Top) | không |
| lookup | Tìm trên web, có chế độ tin tức (`topic=news`) | không |
| fetch | Đọc nội dung một URL | không |
| format | Trình bày kết quả thành bản tin | không |
| send | Gửi văn bản lên Telegram, chỉ khi `confirmed=true` | không |
| policy | Tra cứu tài liệu chính sách nội bộ | không |
| papers | Tìm bài báo trên arXiv | không |
| paper_text | Lấy text của một bài arXiv | không |
| redact | Che email, số điện thoại, API key, token trong đoạn text | có |
| weather | Dự báo thời tiết và nhiệt độ theo địa điểm (Tavily) | có |
| hn_search | Tìm thảo luận trên Hacker News, sắp xếp theo liên quan hoặc mới nhất | có |
| github_search | Tìm repo GitHub, sắp xếp theo sao, cập nhật hoặc khớp nhất | có |

### A3. Câu hỏi mẫu để thử

Đây là 5 câu hỏi mẫu để thử

1. `Tìm kiếm các tin tức AI mới nhất trong tuần qua về OpenAI và DeepSeek.`
2. `Thời tiết hôm nay tại Hà Nội thế nào?`
3. `Trên Hacker News tuần này mọi người đang bàn gì về AI agent evaluation?`
4. `Tìm repo Python về đánh giá AI agent trên GitHub.`
5. `Hãy kiểm tra và che dữ liệu nhạy cảm: Email là dev@corp.com và Token là sk-live-987654321.`

## 3. Giải pháp

**System prompt** ([system_prompt.md](../../starter_v0/artifacts/system_prompt.md)), thay đổi qua các version:
- **v1:** khi thiếu tên tài khoản hoặc URL, không được đoán, phải hỏi lại bằng `clarify`.
- **v2:** trước khi gửi, bắt buộc hỏi xác nhận yes/no bằng `clarify(response_type="yes_no")`.
- **v3:** khi hỏi thông tin còn thiếu, dùng `response_type="text"`.
- **v4:** cho phép gọi tool song song; tin tức dùng `topic="news"`; khi có URL thì đọc trực tiếp bằng `fetch`.
- **v5:** quy tắc thời tiết: chỉ gọi `weather` khi có địa danh thật; các từ chỉ thời gian ("mai", "hôm nay") không được coi là địa điểm.
- **v6:** không đổi prompt, chỉ thêm `github_search` vào tools.

**Tool declarations** ([tools.yaml](../../starter_v0/artifacts/tools.yaml)):
- Bốn tool do nhóm thêm có mô tả đầy đủ "khi nào dùng, khi nào không dùng" và quy ước tham số (ví dụ `hn_search.sort_by = date` khi user nói "mới nhất"; `github_search.language` chỉ điền khi user nêu ngôn ngữ).
- **Hạn chế:** mô tả của 10 tool của starter (`clarify`, `send`, `lookup`, v.v.) vẫn là bản gốc, ngắn và chưa nói rõ khi nào dùng/không dùng

**Tool mới của nhóm** (mỗi tool có `tool.py`, `TOOL.md`, đăng ký trong `tools/__init__.py`, và ≥3 unit test):
- `redact`: gọi trước khi đưa dữ liệu có PII/secret vào tool khác hoặc đăng lên kênh. Chỉ trả về loại và số lượng đã che, không trả lại giá trị gốc.
- `weather`: gọi khi user hỏi thời tiết tại một địa danh cụ thể.
- `hn_search`: gọi khi user nhắc Hacker News hoặc "HN". Không dùng cho X hoặc tin tức web.
- `github_search`: gọi khi user hỏi repo, thư viện, framework hoặc code mẫu. Không dùng cho thảo luận cộng đồng (dùng `hn_search`)

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ [version_log.csv](../../starter_v0/artifacts/version_log.csv). Mỗi version chỉ đổi một artifact (prompt hoặc tools). Thay đổi bộ eval không tính là đổi artifact.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo điểm gốc của starter | — | 0.65 | `runs/v0_B_base_openai_20261110T165343770506.json` |
| v1 | system_prompt.md | Thiếu tài khoản/URL thì phải hỏi lại bằng `clarify` | 0.65 | 0.85 | `runs/v1_B_base_openai_20261110T174106679471.json` |
| v2 | system_prompt.md | Bắt buộc xác nhận yes/no trước khi `send` | 0.85 | 0.90 | `runs/v2_B_base_openai_20261110T175016805712.json` |
| v3 | system_prompt.md | Thêm `response_type="text"` cho `clarify` khi thiếu thông tin | 0.90 | 0.90 | `runs/v3_B_base_openai_20261110T180202454364.json` |
| v4 | system_prompt.md | Cho gọi song song; `topic="news"`; đọc URL trực tiếp | 0.90 | 1.00 | `runs/v4_B_base_openai_20261110T180939839650.json` |
| v4_group | tools.yaml (3 tool mới) | Tool mới route đúng trên bộ 10 case nhóm | 1.00 | 0.90 | `runs/v4_B_group_openai_20261110T193503475832.json` |
| v5_base | system_prompt.md | Quy tắc hỏi địa điểm cho weather | 1.00 | 1.00 | `runs/v5_B_base_openai_20261110T194838786117.json` |
| v5_group | system_prompt.md | Cùng nội dung v5, chạy trên bộ nhóm | 0.90 | 1.00 | `runs/v5_B_group_openai_20261110T194637124609.json` |
| v6_base | tools.yaml (thêm `github_search`) | Thêm tool không làm hỏng routing trên bộ base | 1.00 | 1.00 | `runs/v6_B_base_openai_20261110T211028913950.json` |
| v6_group | tools.yaml + bộ nhóm (2 case đổi sang GitHub) | `github_search` route đúng và giữ được ràng buộc ngôn ngữ | 1.00 | 1.00 | `runs/v6_B_group_openai_20261110T210201837690.json` |

Về bộ tool: v0–v4 dùng bộ tool gốc (`tools_hash` `e69bc5…`). Từ v4_group trở đi dùng bộ có 3 tool nhóm (`9141f4…`), và v6 thêm `github_search` (`2c9e65…`)

### B2. Failure Analysis

Lấy từ `results[*].result` trong run v0 (`runs/v0_B_base_openai_20261110T165343770506.json`). 7/20 case lỗi. `multiturn_accuracy` = 1.0.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix (version đầu tiên pass) |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool / wrong_arg_value | `lookup(query="AI news", topic="news", timeframe="day")` | Query dài hơn kỳ vọng (`AI`) | Pass từ v1 |
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x² là …")` | Gọi `send` cho câu hỏi kiến thức chung | Pass từ v1 |
| R14_out_of_scope_coding | out_of_scope | `send(text="def fibonacci…")` | Gọi `send` cho yêu cầu viết code | Pass từ v1 |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Đoán tên tài khoản thay vì hỏi lại | Pass từ v1 (v1: cấm đoán tài khoản/URL) |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | Bịa URL | v1 pass, v2 fail, **v3 pass** (`response_type="text"`) |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin này")` | Gửi không hỏi xác nhận | **v2 pass** (xác nhận yes/no) |
| R13_parallel_web_and_tweets | wrong_tool / wrong_arg_value | `lookup(query="AI news")` thiếu `topic`, cộng `social_search` | Thiếu `topic=news`, không gọi song song đúng | v1–v3 fail, **v4 pass** (song song + `topic=news`) |

### B3. Team Eval Cases

Bộ [eval_group.json](../../starter_v0/data/eval_group.json) có đúng 10 case: 5 single turn và 5 multi turn. Kết quả lấy từ run v6_group (`runs/v6_B_group_openai_20261110T210201837690.json`), tất cả 10/10 PASS.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_hn_route_timeframe | "HN" và "tuần này" | `hn_search(timeframe=week)` | PASS |
| G02_github_route_language | Hỏi repo, ngôn ngữ Python | `github_search(language=Python)` | PASS |
| G03_weather_tomorrow | Thời tiết ngày mai | `weather(timeframe=tomorrow)` | PASS |
| G04_redact_before_share | Che email/SĐT trước khi gửi khách | `redact` | PASS |
| G05_weather_general_knowledge | Có chữ "mưa" nhưng là kiến thức chung | Không gọi tool | PASS |
| M01_weather_fill_location | Lượt 1 thiếu địa điểm, lượt 2 bổ sung | `weather(timeframe=week)` | PASS |
| M02_weather_ask_location | Không có địa điểm ở mọi lượt | `clarify` (text) | PASS |
| M03_hn_carry_constraints | Ràng buộc qua 3 lượt | `hn_search(timeframe=month, sort_by=date)` | PASS |
| M04_redact_not_policy | Làm sạch đoạn text cụ thể | `redact`, không gọi `policy` | PASS |
| M05_github_carry_language | Lượt 2 bổ sung ngôn ngữ | `github_search(language=TypeScript)` | PASS |

### B4. Live Chat Evidence

Lấy từ [v6_openai_20261110T213759077248.transcript.json](../../starter_v0/transcripts/v6_openai_20261110T213759077248.transcript.json). Phiên được tạo qua UI, provider `openai`, nhãn `v6`, prompt `ddaf2585…`, tools `2c9e6585…`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tin tức AI tuần qua về OpenAI và DeepSeek | `lookup` ×2 | v4 rule song song + `topic=news` | Trả lời có nguồn, nhưng bằng tiếng Anh dù user viết tiếng Việt |
| 2 | "Lấy các bài đăng gần đây của tài khoản này" | Không | v1 rule thiếu tài khoản | Hỏi lại tên tài khoản. Hỏi bằng text, không qua `clarify` |
| 3 | "Tài khoản @sama nhé" | `timeline` | — | Trả về bài đăng của @sama |
| 4 | "Gửi bản tin tóm tắt lên Telegram" | Không | v2 rule xác nhận | Hỏi xác nhận bằng text, **không** qua `clarify(yes_no)` như prompt yêu cầu. Đúng ý (hỏi trước khi gửi), sai cơ chế |
| 5 | "Đồng ý, gửi ngay" | `send` | v2 | Không gửi được: báo thiếu `TELEGRAM_BOT_TOKEN`. Bonus Telegram chưa đạt |
| 6 | Thời tiết hôm nay tại Hà Nội | `weather` | v5 rule địa điểm | Trả về nhiệt độ và tình trạng thời tiết |
| 7 | Che email và token trong đoạn text | `redact` | tool mới | Email và token đã được che |
| 8 | HN tuần này về AI agent evaluation | `hn_search` | tool mới | Trả về danh sách thảo luận trên HN |
| 9 | Repo Python về đánh giá AI agent | `github_search` | tool mới | Trả về danh sách repo |

Các lượt 2, 4 và 5 là điểm cần lưu ý khi chấm: hành vi "hỏi lại" và "xác nhận" xuất hiện, nhưng qua text chứ không qua tool. Lượt 1 trả lời bằng tiếng Anh cho câu hỏi tiếng Việt.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới `weather` | `starter_v0/tools/weather/tool.py`, `TOOL.md` | Tìm kiếm và tổng hợp dự báo qua Tavily Search API | Lỗi trả về error dict (`tool`, `error`, `message`), không raise |
| Tool mới `redact` | `starter_v0/tools/redact/tool.py`, `TOOL.md` | Che email, SĐT, API key; trả về loại và số lượng | Không trả lại giá trị gốc; test kiểm tra không còn secret nào trong kết quả |
| Tool mới `hn_search` | `starter_v0/tools/hn_search/tool.py`, `TOOL.md` | Gọi Algolia HN, map kết quả, giới hạn số lượng | Input xấu được chuẩn hóa; lỗi HTTP/timeout trả error dict |
| Tool mới `github_search` | `starter_v0/tools/github_search/tool.py`, `TOOL.md` | Gọi GitHub Search API, map repo, dựng query `language:`/`pushed:` | Lỗi 403/rate limit và timeout trả error dict; không gửi token nếu không có |
| Unit test (≥3/tool) | `starter_v0/tests/test_tools_todo.py` | 12 test cho 4 tool (3/tool); `pytest` = 94 passed, 14 skipped | 14 skip là stub của tool starter, chưa làm |
| UI (lệnh chạy + link) | `starter_v0/app.py` | Lệnh ở A1; link ở A1; transcript v6 (B4) | Link tạm thời; UI không có đăng nhập |
### B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | | | |
| Hơn 3 tool mới (≥ 4) | 4 tool trong `tools/` (B5a) | Mỗi tool có `TOOL.md`, đăng ký, ≥3 test, và ≥1 eval case route tới (G01–G05, M01–M05) |  |
| `send` gửi thật lên Telegram sau xác nhận | Transcript v6 lượt 5 | Chưa gửi được | Thiếu `TELEGRAM_BOT_TOKEN`; agent chưa dùng `clarify(yes_no)` để xác nhận (B4) |
| Test challenge (0 skipped) | `pytest` | Chưa đạt | 14 stub của tool starter còn `skip` |

### B7. Small Local Model Challenge (bonus)

- Nhóm em không làm ạ

## 5. Khó khăn và cách xử lý

1. **Run `v3_B_group_openrouter_20261110T190340921848.json` lỗi provider 10/10** (`Missing API key env var: OPENROUTER_API_KEY`). Run này không hợp lệ theo RUBRIC (`provider_error_cases` = 10, `measured_cases` = 0), nên không dùng làm bằng chứng. Run cũng có prompt của v4 nhưng gắn nhãn v3. Nhóm giữ file để minh bạch và không tính vào bất kỳ metric nào
2. **Link tunnel.** Cloudflare quick tunnel không có cam kết uptime và đổi link mỗi lần chạy lại. Để demo cần giữ cả Streamlit và `cloudflared` đang chạy

## 6. Tổng hợp đóng góp

Chi tiết phân công và đóng góp cụ thể của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các file báo cáo cá nhân trong thư mục `report/team/`:
- Vũ Thành: [2A202603930_VuThanh.md](2A202603930_VuThanh.md)
- Nguyễn Thành Nam: [2A202603934_NguyenThanhNam.md](2A202603934_NguyenThanhNam.md)
- Vũ Huy Hiệu: [2A202603979_VuHuyHieu.md](2A202603979_VuHuyHieu.md)
- Đỗ Việt Anh: [2A202603973_DoVietAnh.md](2A202603973_DoVietAnh.md)

## 7. Hạn chế và hướng cải thiện — B6. Reflection

**Fix nào thuộc `system_prompt.md`?** Các fix v1–v5 (B2): hỏi lại khi thiếu thông tin, xác nhận trước khi gửi, song song và `topic=news`, quy tắc địa điểm cho weather. Các fix này đã được đo: metric trên bộ base từ 0.65 lên 1.00

**Fix nào thuộc `tools.yaml`?** Mô tả đầy đủ cho bốn tool nhóm (B5a). Phần còn thiếu lớn: mô tả của 10 tool starter vẫn là bản gốc

**Failure cần review thủ công?**
- Lượt 4 của transcript (B4): agent hỏi xác nhận bằng text thay vì `clarify(yes_no)`. Eval hiện không kiểm tra cơ chế này, nên chấm tự động sẽ bỏ sót.
- Lượt 1: trả lời tiếng Anh cho câu hỏi tiếng Việt. Eval không bắt lỗi này
- Lượt 1 và các câu trả lời có link: nên kiểm tra link và nội dung có khớp kết quả tool không

**Nếu có thêm một vòng, nhóm sẽ thử:**
- (a) Viết lại mô tả tool của starter (`send`, `clarify`, `lookup`, `fetch`) theo quy tắc "khi nào dùng/không dùng", như `tools.yaml` 
- (b) Ép `send` đi qua `clarify(yes_no)` trong prompt, để lượt 4 khớp với quy tắc đã viết
- (c) Thêm quy tắc trả lời cùng ngôn ngữ với người dùng, và đo bằng một case eval mới

## 8. Tài liệu tham khảo
- Cloudflare Tunnel (quick tunnel): https://developers.cloudflare.com/cloudflare-one/connections/connect-apps
