# Team

## Thông tin nhóm

- Tên nhóm: NiceTry
- Lớp: L3B
- Repo nhóm: K5-L3B-DAY03-NiceTry-ResearchAgentToolEval
- URL repo, nhánh nộp, commit chốt: https://github.com/Vuthanh2508/K5-L3B-DAY03-NiceTry-ResearchAgentToolEval (nhánh `main`, commit chốt: [điền hash khi nộp])

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |Vũ Thành|2A202603930|       |Vuthanh2508|Baseline và phân tích lỗi (CP1), tối ưu prompt v1–v5 (CP2), eval nhóm, version log và demo (CP5)|
|   2 |Nguyễn Thành Nam|2A202603934|       |        ||
|   3 |Vũ Huy Hiệu|2A202603979|       |        ||
|   4 |Đỗ Việt Anh|2A202603973|dovietanh240405@gmail.com|vietahnn|Team tool `redact` và unit test (CP3), refactor giao diện Streamlit (CP5)|

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## HoVaTen-MSSV

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
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