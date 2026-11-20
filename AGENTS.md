# AGENTS.md — Quy tắc làm việc cho AI Agent (Harness v1.1)

Dự án: **Đảo Đèn Lồng** (Day 12 AI SDLC) — **Phase 2 (Ticket-02)**
Sinh viên: **Đoàn Văn Hiệp** — MSSV: **2A202603565**

## 1. Nguyên tắc cốt lõi
- **Test Contract v1.1 là tối thượng:** Khai báo phiên bản `"contract_version": "1.1"`.
- **Đầy đủ 3 Đêm:** `--night` nhận giá trị `1`, `2`, `3`.
- **Snapshot mở rộng bắt buộc:**
  - `night`, `wind: {active, dir_deg}`
  - `player`: `vel`, `grounded`, `invuln`, `dash_cd_s`, `pulse_cd_s`, `charm_s`
  - Các mảng bắt buộc: `motes`, `shades`, `drifters`, `charms`, `lanterns`, `motes_active`.
- **Trạng thái Bóng Mực chuẩn hóa:** Bắt buộc dùng đúng 5 tên trạng thái: `spawning`, `wander`, `chase`, `recoil`, `stunned`.
- **Thứ tự 12 bước trong mỗi tick:** Đọc input/pause $\rightarrow$ Giảm bộ đếm $\rightarrow$ Di chuyển Mây/rơi đảo $\rightarrow$ Nhặt đom đóm/bùa $\rightarrow$ Nạp đèn $\rightarrow$ Cập nhật vùng an toàn $\rightarrow$ Tỏa Sáng $\rightarrow$ Di chuyển quái/Gió Lạc $\rightarrow$ Chạm/sát thương $\rightarrow$ Sinh thực thể theo lịch $\rightarrow$ Xét thắng/thua $\rightarrow$ Ghi snapshot.

## 2. Các lệnh quan trọng
- **Chạy game 3D trực quan:** `python run_game.py`
- **Chạy chế độ Headless:**
  `python run_headless.py --seed 42 --night 1 --ticks 600 --out test.jsonl`
- **Chạy bộ kiểm thử tự động:** `python -m unittest discover -s tests -p "test_*.py"`
