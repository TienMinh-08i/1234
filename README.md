# Marshmallow Data Prep — gói chuẩn bị dữ liệu độc lập

Gói nguồn riêng, ngày 20/10/2026. Chạy lấy hàm có docstring, ghép test thực sự gọi hàm, lọc test bằng hai probe, chọn phạm vi mutation và tạo corpus mutant offline. Không có model, API key, sinh assertion, experiment A/B/C/D hoặc vòng đánh giá chính.

Mặc định `all` dừng sau khi chuẩn bị dataset. Tạo mutant là bước tùy chọn, cần Docker.

## 1. Cài đặt trong môi trường riêng

Giải nén, mở terminal tại thư mục có `run.py` và dùng Python 3.11 trở lên. Các lệnh dưới đây dùng PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py --help
```

Không cần cài gói vào môi trường của code chính. Nếu muốn có lệnh `mm-data-prep`, có thể chạy `pip install -e .` trong chính `.venv` này; `run.py` đã hoạt động mà không cần bước đó.

Chuẩn bị checkout Marshmallow riêng:

```powershell
git clone https://github.com/marshmallow-code/marshmallow.git checkouts/marshmallow
git -C checkouts/marshmallow checkout 60a803821466f3e537fa2729d65e1aaf7df9d2a4
.\.venv\Scripts\python.exe run.py doctor --repo checkouts/marshmallow
```

Có thể dùng checkout có sẵn ở ngoài gói. Sửa đường dẫn `repo` trong config. Các đường dẫn tương đối trong config được tính từ **thư mục chứa config**. Không đặt đầu ra bên trong checkout hoặc thư mục đầu vào.

## 2. Một lệnh để chuẩn bị dataset

Đọc/sửa `configs/marshmallow.example.json` trước khi chạy. Config ghim commit cũ để đối chiếu; mặc định lấy hàm có docstring, không giới hạn theo tài liệu `.rst`.

```powershell
.\.venv\Scripts\python.exe run.py all --config configs/marshmallow.example.json
```

Kết quả ở `work/marshmallow_run01/`:

```text
raw/         candidates, nodeid chính xác, trace và log ban đầu
prepared/    dataset đã lọc và bằng chứng của từng hàm
pipeline_summary.json
```

Config mẫu có **một exclusion ghi rõ lý do** cho `test_from_timestamp_with_overflow_value`, nhằm giữ lựa chọn lịch sử trên Windows. Đây không phải lọc ngầm trong extractor mới. Xóa entry đó để trace cả test này. Thay exclusions phải dùng đầu ra mới vì fingerprint thay đổi.

Muốn debug nhanh một phần, thêm `tasks` và/hoặc `tests` vào config, ví dụ:

```json
{
  "repo": "../checkouts/marshmallow",
  "output": "../work/pilot",
  "tasks": ["marshmallow.class_registry.get_class"],
  "tests": ["tests/test_registry.py::test_can_use_full_module_path_to_class"],
  "pytest_timeout": 120
}
```

## 3. Chạy riêng từng bước để debug

```powershell
.\.venv\Scripts\python.exe run.py extract --repo checkouts/marshmallow --output work/manual/raw
.\.venv\Scripts\python.exe run.py prepare --repo checkouts/marshmallow --raw work/manual/raw --output work/manual/prepared
.\.venv\Scripts\python.exe run.py validate --repo checkouts/marshmallow --raw work/manual/raw --dataset work/manual/prepared
.\.venv\Scripts\python.exe run.py inspect --output work/manual/prepared
```

`extract` không tự bỏ test overflow. Nếu muốn áp dụng exclusions lịch sử ở chế độ chạy riêng, truyền `--exclude-config` với file JSON chứa list `{pattern, reason}`. Không nhầm file list này với config `all`.

`extract --task ... --test ...` cho phép chọn đúng hàm/test; có thể lặp tùy chọn. `--documented-only` chỉ giữ hàm được nhận diện trong tài liệu `.rst`, thường làm giảm số lượng. `--expected-commit` kiểm tra HEAD trước khi trace. `--timeout` của extract là giới hạn toàn lượt trace, của prepare là giới hạn batch pytest.

Xem đầy đủ traceback:

```powershell
.\.venv\Scripts\python.exe run.py --traceback prepare --repo checkouts/marshmallow --raw work/manual/raw --output work/manual/prepared
```

Mỗi bước chỉ ghi thư mục đầu ra của nó. `prepare` không gọi extraction lại. `scope` không lọc test lại. `mutants` chỉ đọc scope đã có.

## 4. Chọn callee và tạo mutant, khi cần

Khởi động Docker Desktop Linux containers, sau đó:

```powershell
docker build -f Dockerfile.mutmut -t mm-data-prep-mutmut:0.1.0 .
.\.venv\Scripts\python.exe run.py doctor --docker
.\.venv\Scripts\python.exe run.py scope --repo checkouts/marshmallow --dataset work/manual/prepared --output work/manual/scope
.\.venv\Scripts\python.exe run.py mutants --repo checkouts/marshmallow --scope work/manual/scope --output work/manual/mutants
.\.venv\Scripts\python.exe run.py validate --repo checkouts/marshmallow --dataset work/manual/prepared --scope work/manual/scope --mutants work/manual/mutants
```

Hoặc chạy tiếp pipeline đã có bằng:

```powershell
.\.venv\Scripts\python.exe run.py all --config configs/marshmallow.example.json --resume --through mutants
```

Quy tắc: thân hàm sau chuẩn hóa AST, bỏ docstring, **<5 dòng** thì lấy hàm và callee nội bộ trực tiếp, chỉ một tầng. Hàm >=5 dòng chỉ mutation tại hàm. Không lấy tiếp callee của callee. Scope lưu riêng `observed` và `lexical_unobserved`; candidate lexical chưa được quan sát không bị mô tả nhầm là đã phủ test.

Docker dùng Python 3.12 và mutmut 2.5.1. Source của gói và checkout được mount read-only ở hai đường riêng, nên checkout không cần nằm trong workspace. Corpus được ghi vào output. Không dùng Docker image của vòng đánh giá chính.

## 5. Đọc và kiểm tra output

| File | Nội dung |
|---|---|
| `raw/problems.jsonl` | Tất cả candidate có docstring, có module/class/path/decorator/source; giữ cả candidate chưa ghép test để audit |
| `raw/tests.jsonl` | Một cặp hàm–test mỗi dòng, lưu nguyên nodeid kể cả IPv6/Unicode và tham số `::` |
| `raw/trace.json`, `trace.log`, `command.json` | Test đã collect, quan hệ gọi, kết quả setup/call/teardown và lệnh đã chạy |
| `raw/summary.json` | Candidate, linked, test links và hàm chưa có test |
| `prepared/problems.jsonl`, `tests.jsonl` | Bộ dùng được sau lọc |
| `prepared/excluded_functions.json` | Hàm bị loại và lý do |
| `prepared/functions/<hash>/input.json` | Đầu vào riêng cho từng hàm |
| `prepared/functions/<hash>/filter.json` | Quyết định giữ/bỏ từng test cùng evidence của hai probe |
| `prepared/functions/<hash>/arms/*.json` | Trạng thái pytest, số checks/violations và log để debug |
| `scope/scope.json`, `targets.json` | Hàm gốc, số dòng thân hàm và callee được chọn |
| `mutants/functions.json` | Mutant theo hàm, `kind=self/callee`, `mutation_target`, `function_source`, `diff` |
| `mutants/targets/<hash>/export.json` | Kết quả export từng target, gồm mutant đã bỏ qua và lý do |
| `manifest.json` tại từng bước | Fingerprint, nguồn và hash artifact; chỉ complete khi bước hoàn tất |

Lọc test: pass với `assert True`, rồi có assertion violation gây fail ở **call phase** khi dùng `assert False`; setup và teardown phải pass, không có lỗi runtime của postcondition. Test bắt/nuốt AssertionError không được giữ. Test ném exception trước return không được dùng làm bằng chứng postcondition sau return. Các cuộc gọi chỉ diễn ra ở setup không được ghép vào raw.

Trace raw có thể ghi nhận test đang fail trên source gốc. Bước prepare sẽ loại chúng; raw không tự tuyên bố test đã pass.

## 6. Resume và tính tái lập

Thêm `--resume` vào đúng bước/lệnh đang chạy. Thư mục đã có kết quả không được ghi đè ngầm. Thay source, test, selector, timeout, code hoặc môi trường có thể khiến fingerprint khác; dùng thư mục mới. Nếu collection bị ngắt trước checkpoint, engine yêu cầu đầu ra mới; không tự coi collection dở dang là hợp lệ. `--force` của prepare yêu cầu chạy lại probe và vẫn cần `--resume` khi output đã có manifest.

Các manifest ghim đường checkout và môi trường Python/package. Sao chép output sang máy khác không đồng nghĩa tái sử dụng cache được ngay. `validate` chỉ đọc/kiểm tra, không chạy pytest, Docker hoặc LLM.

## 7. Kiểm thử gói

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
```

Test dùng checkout giả trong thư mục tạm, kiểm tra nodeid IPv6, lọc hai probe, property/private method, callee một tầng, guard đường dẫn, resume và tính độc lập import. Test Docker dùng worker giả để kiểm tra mount/mapping; không thay thế việc chạy mutmut thật trong container. Xem `VALIDATION.md` về các kiểm tra đã thực hiện khi bàn giao.

## 8. Cấu trúc và ranh giới với code chính

```text
run.py                       đầu vào đơn giản từ source ZIP
configs/                     cấu hình đầu vào, selector, exclusion và timeout
src/mm_data_prep/
    cli.py                   điều phối các bước
    extract.py               extraction giữ nodeid chính xác
    trace_plugin.py          ghép hàm–test trong call phase
    _engine/                 snapshot runtime offline đã có
tests/                       kiểm thử riêng của gói
Dockerfile.mutmut             image export mutant riêng
UPSTREAM_SNAPSHOT.json       nguồn, hash và ghi chú thích ứng
```

Không import `paper_eval_v2`, `specmind_test`, OpenAI hoặc code trong `tmp`. `_engine/extract_legacy.py` chỉ được dùng cho helper đọc `.rst` khi bật `--documented-only`; các entry point trace/export legacy không được gọi. Chưa nối gói này vào code chính hoặc thay bộ dữ liệu hiện tại. Trước khi tích hợp sau này cần đối chiếu tên hàm, test nodeid, source, scope và mutant, thay vì chỉ so tổng số lượng.

59 candidate/57 hàm prepared là số của snapshot lịch sử. Gói mới đã hỗ trợ property/private method, nên không ép giữ đúng 57 hoặc cam kết xuất cùng 352 mutant. Số cuối phụ thuộc commit, bộ test, môi trường và exclusions. Mọi chênh lệch cần đọc từ manifest và excluded list.
