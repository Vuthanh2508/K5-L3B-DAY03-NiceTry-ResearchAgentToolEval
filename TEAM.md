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
|   4 |Đỗ Việt Anh|2A202603973|       |        ||

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