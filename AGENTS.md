# AGENTS.md — Quy tắc làm việc cho AI Agent (Harness v1.2)

Dự án: **Đảo Đèn Lồng** (Day 12 AI SDLC) — **Phase 3 (Ticket-03 "Đèn cạn dầu")**
Sinh viên: **Đoàn Văn Hiệp** — MSSV: **2A202603565** — Lớp: **K5-L3A**

## 1. Nguyên tắc cốt lõi (Contract v1.2)
- **Test Contract v1.2 là tối thượng:** Khai báo phiên bản `"contract_version": "1.2"`.
- **Hệ thống Nhiên liệu Đèn:**
  - `fuel_max = 100`, hao hụt tự nhiên $1.0$ đơn vị/giây (1/60 mỗi tick).
  - Vùng an toàn 6m chỉ có hiệu lực khi `fuel >= 30.0`.
  - Hết dầu phát sinh sự kiện `lantern_out` (`reason: "fuel_empty"`). Đèn nhớ cờ `ever_lit = True`.
  - Thắp lại đèn đã tắt chỉ tốn **5 đom đóm**, thưởng +40 điểm.
  - Châm dầu cho đèn đang sáng tốn đom đóm hồi phục 10 fuel/đom, phát sự kiện `refuel`.
- **Trạng thái Bóng Mực mở rộng (6 trạng thái):**
  - Bắt buộc dùng đúng 6 tên: `spawning`, `wander`, `chase`, `recoil`, `stunned`, `drain`.
  - Khi ở `wander`, Bóng Mực tìm đến đèn yếu (`fuel < 30.0`) gần nhất $\le 2$m chuyển sang `drain`, hút $5.0$ fuel/giây và phát sự kiện `fuel_drain`.
- **Thắng / Thua theo Bình Minh (Dawn Survival):**
  - **Không còn thắng sớm khi thắp hết đèn.**
  - Thắng khi hết thời gian Đêm và số đèn sáng $\ge \lceil 0.6 \times \text{tổng đèn} \rceil$ (`reason: "dawn_survived"`).
  - Thua khi mất hết ngọn lửa (`reason: "no_flames"`), hết giờ không đủ 60% đèn sáng (`reason: "dawn_insufficient_light"`), hoặc bế tắc tuyệt đối (`reason: "darkness"`).
- **Sức chứa Đom Đóm Động (Dynamic Capacity):**
  - Khởi đầu 10 đom đóm. Mỗi lần thắp đèn thành công tăng vĩnh viễn +2 sức chứa (tối đa 20 đom đóm).
  - `lantern_lit` bắt buộc chứa trường `"new_capacity"`.
- **Thứ tự 12 bước trong mỗi tick:**
  1. Đọc input / Pause processing.
  2. Giảm bộ đếm & Hao hụt/hút nhiên liệu đèn.
  3. Di chuyển Mây (Nhảy, Lướt, Bục nhảy, Gió, Rơi vực).
  4. Nhặt đom đóm & Bùa Gió.
  5. Tương tác đèn (Nạp đom đóm / Châm dầu).
  6. Cập nhật vùng an toàn (chỉ khi `fuel >= 30`).
  7. Tỏa Sáng (Pulse).
  8. Di chuyển Bóng Mực (Wander, Chase, Drain) & Gió Lạc.
  9. Chạm / Sát thương (Gió Lạc cướp trước, Bóng Mực gây sát thương sau).
  10. Sinh thực thể theo lịch trình.
  11. Xét thắng / thua (No flames, Darkness deadlock, Dawn survival).
  12. Ghi snapshot theo chu kỳ `--snapshot-every`.

## 2. Các lệnh quan trọng
- **Chạy game 3D trực quan:** `python run_game.py` (truy cập `http://localhost:8000/web/`)
- **Chạy chế độ Headless:**
  `python run_headless.py --seed 42 --night 1 --ticks 600 --out test.jsonl`
- **Chạy bộ kiểm thử tự động:**
  `python -m unittest discover -s tests -p "test_*.py"`
