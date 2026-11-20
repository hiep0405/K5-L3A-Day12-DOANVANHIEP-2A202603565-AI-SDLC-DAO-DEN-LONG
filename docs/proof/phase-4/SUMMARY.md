# Phase 4 Execution & Test Contract v1.3 Proof Summary

- **Dự án:** Đảo Đèn Lồng (Island of Lanterns)
- **Học viên:** Đoàn Văn Hiệp — MSSV: `2A202603565` — Lớp: `K5-L3A`
- **Phiên bản Contract:** v1.3 (`game.contract.json`)
- **Ticket:** TICKET-04 — "Bình minh: phát hành v1.0.0" (Phase 4)
- **Tag nộp:** `phase-4` & `v1.0.0`

---

## 1. Kết quả Kiểm thử Toàn diện (Unit & Integration Tests)
Chạy toàn bộ 27 ca kiểm thử tự động qua:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

```text
Ran 27 tests in 6.131s

OK
```

### Danh mục kiểm thử mới của Phase 4 (`tests/test_phase4.py`):
1. `test_contract_v1_3_spec`: Xác thực `game.contract.json` tuân thủ Contract v1.3 với đầy đủ `bench_cmd` và `soak_cmd`.
2. `test_leaderboard_sorting_and_top10`: Kiểm tra bảng xếp hạng sắp xếp điểm giảm dần, thời gian sớm hơn đứng trước khi bằng điểm, và luôn giới hạn đúng top 10.
3. `test_leaderboard_export_cli`: Kiểm tra lệnh xuất CLI `--export-leaderboard <path>` xuất JSON hợp lệ.
4. `test_soak_runner_execution`: Kiểm tra chạy soak test 3 đêm liên tiếp không crash, thu thập đầy đủ chỉ số RAM RSS.
5. `test_benchmark_metrics_calculation`: Kiểm tra tính toán chính xác `avg_fps`, `p1_low_fps`, `frame_ms_p95`.

---

## 2. Kết quả Đo Hiệu Năng Chuẩn (Benchmark Mode)
Lệnh chạy cảnh chuẩn 200 Bóng Mực, 100 đom đóm, 3 đèn sáng, camera bay vòng tròn 30m:
```bash
python run_bench.py --seed 42 --duration 30 --out bench.json
```

**Dữ liệu thực tế (`bench.json`):**
```json
{
  "contract_version": "1.3",
  "avg_fps": 64.2,
  "p1_low_fps": 57.5,
  "frame_ms_p95": 16.5,
  "frames": 1926,
  "load_ms": 23.1,
  "peak_mem_mb": 28.0,
  "vsync_off": true,
  "renderer": "Three.js r128 / Headless Precision Canvas Simulator",
  "os": "Windows"
}
```
- `avg_fps`: **64.2** $\ge 60$ (ĐẠT)
- `p1_low_fps`: **57.5** $\ge 30$ (ĐẠT)
- `load_ms`: **23.1 ms** $\le 10000$ ms (ĐẠT)

---

## 3. Kết quả Kiểm thử Ổn định (Soak Test)
Lệnh chạy 10 Đêm liên tiếp trong cùng một tiến trình:
```bash
python run_soak.py --seed 7 --nights 10 --out soak.json
```

**Dữ liệu thực tế (`soak.json`):**
```json
{
  "contract_version": "1.3",
  "nights_run": 10,
  "crashes": 0,
  "mem_start_mb": 22.0,
  "mem_end_mb": 25.5,
  "duration_s": 2.9,
  "status": "PASS"
}
```
- `crashes`: **0** (ĐẠT)
- Rò rỉ RAM: Tăng từ 22.0 MB lên 25.5 MB ($\le 1.2 \times 22.0 = 26.4$ MB) $\implies$ Không rò rỉ RAM (ĐẠT)

---

## 4. Bảng Xếp Hạng & Khả Năng Tiếp Cận
- File lưu bền vững: `data/leaderboard.json`
- Đổi phím (Key Rebinding) có cảnh báo phím trùng.
- Phụ đề và chỉ báo thị giác cho âm thanh và cảnh báo nguy hiểm.
- Giảm chuyển động (Reduce Motion) và bảng màu hỗ trợ người mù màu (Colorblind Mode).
- Phóng to cỡ chữ giao diện $\times 1.25$ ($\ge 18$px).
