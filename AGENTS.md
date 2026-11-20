# AGENTS.md — Quy tắc làm việc cho AI Agent (Harness v1.3)

Dự án: **Đảo Đèn Lồng** (Day 12 AI SDLC) — **Bản phát hành chính thức v1.0.0 (Phase 4)**  
Sinh viên: **Đoàn Văn Hiệp** — MSSV: **2A202603565** — Lớp: **K5-L3A**

## 1. Nguyên tắc cốt lõi (Contract v1.3)
- **Test Contract v1.3 là tối thượng:** Khai báo phiên bản `"contract_version": "1.3"` trong `game.contract.json`.
- **Đầy đủ 4 công cụ thực thi chuẩn:**
  - `run_cmd`: `python run_game.py` (Chạy WebGL 3D server hoặc xuất bảng xếp hạng qua `--export-leaderboard <path>`).
  - `headless_cmd`: `python run_headless.py` (Mô phỏng 60 tick/s không giao diện, 100% tất định).
  - `bench_cmd`: `python run_bench.py` (Đo hiệu năng cảnh chuẩn: 200 Bóng Mực, 100 đom đóm, 3 đèn sáng, camera bay vòng tròn).
  - `soak_cmd`: `python run_soak.py` (Kiểm thử ổn định chạy lâu: 10 Đêm liên tiếp cùng tiến trình, kiểm tra rò rỉ RAM).
- **Hệ thống Nhiên liệu Đèn:** `fuel_max = 100`, hao hụt $1.0$/s, đèn tắt khi hết dầu (`ever_lit: True`), thắp lại tốn 5 đom đóm, châm dầu (+10 fuel/đom).
- **Bóng Mực hút dầu:** Trạng thái `drain` khi tiếp cận đèn yếu ($< 30$ fuel), hút $5.0$ fuel/s, Tỏa Sáng trúng Bóng Mực đang drain thưởng +15 điểm.
- **Thắng theo Bình Minh (Dawn Survival):** Thắng khi hết giờ và có $\ge 60\%$ đèn sáng (`dawn_survived`).
- **Sức chứa Đom Đóm Động:** 10 $\to$ tối đa 20 (+2 mỗi lần thắp đèn).
- **Khả năng Tiếp Cận (Accessibility):** Đổi phím tự do, phụ đề cảnh báo, giảm chuyển động, cỡ chữ lớn $\times 1.25$.

## 2. Các lệnh quan trọng
- **Chạy game 3D trực quan:** `python run_game.py`
- **Chạy chế độ Headless:**
  `python run_headless.py --seed 42 --night 1 --ticks 1200 --out test.jsonl`
- **Chạy Benchmark:**
  `python run_bench.py --seed 42 --duration 30 --out bench.json`
- **Chạy Soak Test:**
  `python run_soak.py --seed 7 --nights 10 --out soak.json`
- **Xuất Bảng Xếp Hạng:**
  `python run_game.py --export-leaderboard out.json`
- **Chạy toàn bộ kiểm thử tự động (27 bài):**
  `python -m unittest discover -s tests -p "test_*.py"`
