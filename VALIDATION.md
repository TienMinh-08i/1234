# Kiểm tra bàn giao ngày 20/10/2026

## Đã chạy

- 8 kiểm thử của gói: **8 passed**, 20,95 giây trên Python 3.11.6, pytest 8.4.2, simplejson 3.20.2, tzdata 2025.2.
- Luồng nhỏ hoàn chỉnh trên checkout giả: 6 candidate, 5 hàm prepared; hàm không có test bị loại rõ lý do.
- Giữ nguyên nodeid tham số IPv6 có `::`; không ghép cuộc gọi chỉ xuất hiện trong setup.
- Lọc bỏ test fail gốc, đường ném exception và test nuốt AssertionError.
- Xử lý property và private method; scope một tầng quan sát được cả hai callee.
- Resume tái sử dụng kết quả mà không gọi lại pytest; kiểm tra hash và guard thư mục đầu ra.
- Chạy CLI `all`, `validate` và resume trên bộ nhỏ. Mặc định không tạo scope/mutant.
- Kiểm tra import trong process cô lập: không nạp `paper_eval_v2`, `specmind_test` hoặc OpenAI.
- Worker Docker giả kiểm tra mount checkout bên ngoài gói, read-only source và mapping mutant callee.
- Quét checkout Marshmallow ở commit `60a803821466f3e537fa2729d65e1aaf7df9d2a4`: **59 candidate có docstring**, có `Nested.schema` và `Schema.__apply_nested_option`.
- Chạy thật một hàm `marshmallow.class_registry.get_class` với test `tests/test_registry.py::test_can_use_full_module_path_to_class`: raw 1 liên kết, prepared 1 hàm/1 test, scope 1 target; không có pending.

## Phần chưa chạy lại

- **Không chạy lại toàn bộ 59 hàm hoặc corpus mutant 57 hàm** trong lần đóng gói này.
- Docker Desktop Linux engine không hoạt động khi kiểm tra. Đã kiểm tra cấu trúc lệnh/mapping bằng worker giả, **chưa build image mới hoặc export mutant thật** bằng gói độc lập.
- Không khẳng định đầu ra mới phải giữ 57 hàm hoặc 352 mutant; runtime mới hỗ trợ hai trường hợp trước đây bị loại. Cần so sánh từng record trước khi tích hợp.
- Không benchmark tốc độ hoặc kiểm tra mọi phiên bản Python/hệ điều hành.

`PACKAGE_MANIFEST.json` ghi hash các tệp của gói; `UPSTREAM_SNAPSHOT.json` ghi nguồn code được sao chép. Archive chỉ chứa source, test, config và tài liệu.
