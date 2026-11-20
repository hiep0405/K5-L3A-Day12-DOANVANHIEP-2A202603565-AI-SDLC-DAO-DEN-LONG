# AGENTS.md — Quy tắc làm việc cho AI Agent (Harness)

Dự án: **Đảo Đèn Lồng** (Day 12 AI SDLC)
Sinh viên: **Đoàn Văn Hiệp** — MSSV: **2A202603565**

## 1. Nguyên tắc cốt lõi
- **Test Contract là tối thượng:** Không bao giờ thay đổi các trường dữ liệu, định dạng JSONL, quy ước tọa độ, hay làm sai khác exit code của `run_headless.py`.
- **Tách biệt Core và Renderer:**
  - `src/core/`: Logic game mô phỏng toán học tất định (60 tick/s), không phụ thuộc GPU/Window.
  - `web/`: Giao diện 3D Three.js và âm thanh Web Audio API phục vụ chơi trực quan (`run_game.py`).
- **Không tự ý giả định mà không ghi chép:** Mọi điểm mơ hồ được ghi chép vào `docs/notes/assumptions.md`.
- **Tiết kiệm token:** Giữ ngữ cảnh ngắn gọn, giải quyết theo bước nhỏ, chạy test xác minh ngay sau mỗi lần sửa.

## 2. Các lệnh quan trọng
- **Cài đặt:** `python -m pip install -r requirements.txt` (Zero external dependencies).
- **Chạy game 3D trực quan:** `python run_game.py` (Khởi chạy máy chủ cục bộ và mở trình duyệt).
- **Chạy chế độ Headless:**
  `python run_headless.py --seed 42 --night 1 --ticks 600 --out test.jsonl`
- **Chạy kiểm thử tự động:** `python -m unittest discover -s tests -p "test_*.py"`

## 3. Quy ước tọa độ & Đo lường
- Độ dài tính bằng mét ($m$). Trục $Y$ hướng lên trên; mặt đất đảo ở $Y = 0$.
- Tọa độ người chơi xuất phát mặc định: $(0, 0, 0)$.
- Mọi khoảng cách đo trên mặt phẳng ngang $XZ$: $d = \sqrt{\Delta x^2 + \Delta z^2}$.
- Toạ độ trong snapshot xuất ra làm tròn 3 chữ số thập phân (`round(val, 3)`).
