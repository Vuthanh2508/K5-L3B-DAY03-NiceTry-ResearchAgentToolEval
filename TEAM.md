# Team

## Thông tin nhóm

- Tên nhóm: NiceTry
- Lớp: L3B
- Repo nhóm: K5-L3B-DAY03-NiceTry-ResearchAgentToolEval
- URL repo, nhánh nộp, commit chốt: https://github.com/Vuthanh2508/K5-L3B-DAY03-NiceTry-ResearchAgentToolEval (nhánh `main`, commit chốt: c5431a7)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |Vũ Thành|2A202603930|vuthanhdz2508@gmail.com|Vuthanh2508|Baseline và phân tích lỗi (CP1), tối ưu prompt v1–v5 (CP2), eval nhóm, version log và demo (CP5)|
|   2 |Nguyễn Thành Nam|2A202603934| ishodajo@gmail.com |Ishodayo|Team tool `hn_search` và `github_search` kèm unit test (CP3), viết bộ eval nhóm 10 case (CP4)|
|   3 |Vũ Huy Hiệu|2A202603979|hieuvippro531@gmail.com|hieunhangia|Team tool weather kèm unit test (CP3), xây dựng base UI Streamlit (CP5)|
|   4 |Đỗ Việt Anh|2A202603973|dovietanh240405@gmail.com|vietahnn|Team tool `redact` và unit test (CP3), refactor giao diện Streamlit (CP5)|

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

## VuThanh-2A202603930

### Phần việc phụ trách

- CP1: chạy baseline v0, phân tích 7 case lỗi của v0 và phân loại lỗi
- CP2: tối ưu system prompt qua v1–v5 trên bộ base, metric base từ 0.65 lên 1.00
- CP3: kiểm tra các tool mà nhóm thêm vào
- Version log và eval: ghi các dòng version trong `version_log.csv`; thêm case `github_search` vào bộ eval nhóm
- CP5: UI v6, transcript CP5

### Đóng góp cụ thể
- Chạy các lần fix system_prompt ở CP2, phần tích từng run json từ v0-v6
- version log: viết và phân tích log, dùng số liệu lấy từ run JSON
- Tạo transcript CP5 `v6_openai_20261110T213759077248.transcript.json` gồm 9 lượt bằng UI

### Bằng chứng

- Commit: 8e9dd3b, af09cad, e22e2e4 (email vuthanh250804@gmail.com), 3d44ccf (email vuthanhdz2508@gmail.com) (cả 2 đều là tài khoản github của em), transcript và sửa `app.py`
- folder Run: run v1-v6
- Transcript: v6_openai_20261110T213759077248

## NguyenThanhNam-2A202603934

### Phần việc phụ trách

- CP3: viết 2 team tool `hn_search` (Hacker News) và `github_search` (GitHub), mỗi tool 3 unit test
- CP4: viết bộ eval nhóm `data/eval_group.json` (10 case: 5 single turn, 5 multi turn)

### Đóng góp cụ thể

- `hn_search`: tìm story trên Hacker News qua Algolia API, không cần key; args `query`, `sort_by`, `timeframe`, `limit`; input xấu được chuẩn hóa, lỗi trả error dict
- `github_search`: tìm repo qua GitHub Search API, không bắt buộc key (tự dùng `GITHUB_TOKEN` nếu có); args `query`, `sort_by`, `language`, `timeframe`, `limit`
- 6 unit test offline (happy path, input xấu từ model, nhánh lỗi HTTP/timeout) cho 2 tool
- 10 case eval nhóm phủ `hn_search`, `weather`, `redact` (route tool mới, args quy ước, `no_tool`, hỏi lại khi thiếu thông tin, ràng buộc nhiều lượt); sau đó Vũ Thành đổi 2 case sang `github_search` ở v6

### Bằng chứng

- Commit: `f385305` (hn_search), `7185995` (eval group), `3561737` (github_search)
- `pytest` full: 94 passed, 0 failed, 14 skipped (stub tool starter); contract test xanh
- Báo cáo cá nhân: `report/team/2A202603934_NguyenThanhNam.md`

## VuHuyHieu-2A202603979

### Phần việc phụ trách

- CP3: viết team tool `weather` (tra cứu thời tiết qua Tavily Search API) kèm 3 unit test cho tool này
- CP5: xây dựng giao diện Streamlit cơ bản ban đầu trong `starter_v0/app.py`, cấu hình requirements và sinh transcript chat thử nghiệm

### Đóng góp cụ thể

- Viết `starter_v0/tools/weather/tool.py` (55 dòng) và `starter_v0/tools/weather/TOOL.md`: tra cứu thời tiết qua Tavily Search API. Validate địa điểm rỗng, bắt thiếu API key, xử lý ngoại lệ và trả về error dict thay vì raise. Đăng ký tool trong `starter_v0/tools/__init__.py` và `starter_v0/artifacts/tools.yaml`.
- Viết 3 unit test trong `starter_v0/tests/test_tools_todo.py`: `test_my_new_tool_happy_path` (mock HTTP, kiểm tra endpoint, query và summary), `test_my_new_tool_bad_input_from_model` (địa điểm rỗng trả về ValueError), `test_my_new_tool_failure_returns_error_dict` (thiếu API key trả về RuntimeError).
- Xây dựng file `starter_v0/app.py` (450 dòng) tạo nền tảng giao diện Streamlit UI cho nhóm ở CP5: hỗ trợ đa provider (OpenAI, OpenRouter, Gemini), chọn version prompt/tool, giao diện chat hiển thị tool calls, và tự động xuất transcript JSON. Thêm dependency `streamlit` vào `starter_v0/requirements.txt`.
- Chạy thử nghiệm baseline bổ sung với OpenRouter (`runs/v0_B_base_openrouter_20261110T175509128401.json`) và tạo các transcript chat thử nghiệm đầu tiên.

### Bằng chứng

- Commit: `3111f67` (feat: add weather tool and associated tests and documentation), `9f94e52` (update base UI streamlit)
- File: `starter_v0/tools/weather/tool.py`, `starter_v0/tools/weather/TOOL.md`, `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml`, `starter_v0/tests/test_tools_todo.py`, `starter_v0/app.py`, `starter_v0/requirements.txt`
- Kiểm chứng: `pytest starter_v0/tests/test_tools_todo.py -k test_my_new_tool` → 3 passed; `pytest starter_v0/tests/ -k weather` → 5 passed (contract test); full `pytest starter_v0/tests/` → 94 passed, 14 skipped.
- Báo cáo cá nhân: `report/team/2A202603979_VuHuyHieu.md`

## DoVietAnh-2A202603973

### Phần việc phụ trách

- CP3: viết team tool `redact` (che PII/secret) và 3 unit test cho tool này
- CP5: refactor giao diện Streamlit trong `starter_v0/app.py`

### Đóng góp cụ thể

- Viết `starter_v0/tools/redact/tool.py` (126 dòng) và `starter_v0/tools/redact/TOOL.md`: tool local, không cần API key, không gọi mạng. Che 6 loại dữ liệu nhạy cảm (bearer token, API key, credentials trong URL, secret assignment, email, số điện thoại) bằng một lần quét regex hợp nhất; kết quả chỉ trả về *loại* và *số lượng* đã che, không bao giờ trả lại giá trị gốc nên an toàn khi ghi vào transcript. Tool nhận thêm `extra_patterns` (regex tùy chỉnh của nhóm), validate input lỗi và trả về error dict thay vì raise.
- Đăng ký tool trong `starter_v0/tools/__init__.py` và khai báo trong `starter_v0/artifacts/tools.yaml` với mô tả đủ "khi nào dùng / không dùng".
- Viết 3 unit test trong `starter_v0/tests/test_tools_todo.py`: `test_redact_masks_email_phone_and_api_key` (kiểm tra không còn secret nào sót lại trong mọi string lồng nhau trong kết quả), `test_redact_empty_text_returns_error_dict`, `test_redact_invalid_extra_pattern_returns_error_dict`.
- Refactor `starter_v0/app.py`: gom các khối sidebar (cấu hình provider/model, câu hỏi mẫu CP5) vào `st.expander` đóng mặc định để giao diện gọn và dễ thao tác hơn; 42 dòng thêm, 58 dòng xóa.

### Bằng chứng

- Commit: `2dea30e` (add redact tool), `d3241e4` (remove files - dọn thư mục `venv/` bị commit nhầm), `5e9c5b1` (refactor UI), `89a8975` (PR #1, nhánh `2A202603973_VIETANH`)
- File: `starter_v0/tools/redact/tool.py`, `starter_v0/tools/redact/TOOL.md`, `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml`, `starter_v0/tests/test_tools_todo.py`, `starter_v0/app.py`
- Kiểm chứng: `pytest starter_v0/tests/ -k redact` → 8 passed (3 test của em + 5 test contract tự sinh theo tool). Chạy full `pytest starter_v0/tests/` → 94 passed, 14 skipped (14 skip là stub của 10 tool starter, không thuộc phần em làm)
- AI và công cụ đã dùng: tự viết tool và test; dùng Claude Code để đọc lại code, chạy `pytest` xác minh kết quả thực tế thay vì tự ghi số liệu