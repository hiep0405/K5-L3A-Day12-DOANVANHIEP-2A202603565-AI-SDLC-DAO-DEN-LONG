# Đặc tả Nghiệm thu Phase 2 (Acceptance Criteria — Ticket-02)

Dự án: **Đảo Đèn Lồng (Island of Lanterns)**
Khóa: K5 VinAI — AI SDLC Day 12
Sinh viên: **Đoàn Văn Hiệp** — MSSV: **2A202603565**

## Tiêu chí Nghiệm thu chi tiết cho Phần 3

### 1. Gió Lạc (Drifters) — Đêm 2 & Đêm 3
- [x] **Sinh:** Tối đa 2 con, xuất hiện tại tick 1200, 2400, ... với ID D1, D2, ...
- [x] **Trạng thái:**
  - `idle`: bay chậm 2 m/s.
  - `chase`: chuyển từ `idle` sang `chase` khi Mây mang $\ge 5$ đom đóm và khoảng cách $\le 15m$. Trở về `idle` nếu điều kiện mất.
  - `flee`: kích hoạt sau khi cướp hoặc bị Tỏa Sáng; bay xa 7 m/s trong 240 tick rồi biến mất (`removed`).
- [x] **Cướp đom đóm:** Khi khoảng cách XZ $\le 1.2m$, cướp $\min(3, \text{đang mang})$. Mỗi con cướp đúng 1 lần. Không làm mất Ngọn Lửa, bất tử không chặn cướp.
- [x] **Tác động Tỏa Sáng:**
  - Trúng Gió Lạc đang `chase` $\rightarrow$ chuyển `flee` không cướp.
  - Trúng Gió Lạc đang `flee` có mang đồ $\rightarrow$ thả toàn bộ đom đóm tại chỗ dạng đom đóm rơi (TTL 480 tick), Gió Lạc biến mất sau 120 tick.

### 2. Bùa Gió (Wind Charms)
- [x] **Vị trí:** Đêm 2 tại $(35, 0, 0)$; Đêm 3 tại $(30, 0, 25)$ và $(-30, 0, 25)$.
- [x] **Hiệu lực (600 tick):** Tốc độ chạy tăng lên 7.2 m/s. Lướt không có thời gian hồi chiêu (`dash_cd_ticks = 0`). Nhặt lại làm mới thời gian 600 tick.
- [x] **Hồi sinh:** Xuất hiện lại sau 2700 tick (45 giây) kể từ khi nhặt.

### 3. Chuỗi 3 Đêm (Campaign Mode)
- [x] **Luồng chơi:** Menu chính $\rightarrow$ Giới thiệu Đêm (tên đảo, lời dẫn Ông Đăng) $\rightarrow$ Chơi $\rightarrow$ Kết quả $\rightarrow$ Đêm kế tiếp.
- [x] **Kết thúc:** Thắng Đêm 3 hiển thị màn hình Bình Minh cùng tổng điểm chiến dịch; Thua cho phép chơi lại Đêm đó.

### 4. Tạm dừng (Pause Mechanism)
- [x] **Phím bấm:** Nhấn `P` hoặc `Escape`.
- [x] **Hành vi logic:** Dừng hoàn toàn mô phỏng, `sim_tick`, bộ đếm thời gian, hồi chiêu, TTL, spawn đều đứng yên.
- [x] **Snapshot:** Ghi trường `state: "paused"`.

### 5. Cài đặt (Settings)
- [x] Lưu trạng thái âm lượng và độ nhạy chuột vào `localStorage` giữa các lần mở game.

### 6. Âm thanh Tương tác (Web Audio API)
- [x] Tích hợp âm thanh thuật toán cho: nhặt đom đóm, nạp đèn, thắp sáng đèn, bị đánh, nhảy, lướt, tỏa sáng, thắng, thua.

### 7. HUD Đầy đủ & Chỉ báo
- [x] Ngọn Lửa (trên trái), Đồng hồ mm:ss (đổi màu đỏ nhấp nháy khi $\le 30$s).
- [x] Thanh đom đóm 10 ô trực quan (dưới giữa).
- [x] Biểu tượng hồi chiêu Lướt và Tỏa Sáng kèm overlay tiến độ.
- [x] Dòng chữ nhắc "E — Nạp ánh sáng (x/10)" khi đứng gần đèn lồng.

### 8. Bảng màu Chuẩn (Palette)
- [x] Trời đêm / sương: `#0E1430` / `#1B2350`.
- [x] Cỏ / cát / biển mây: `#2F5D50` / `#C9B48A` / `#12384A`.
- [x] Đèn sáng / lõi / đèn tắt: `#FFB347` / `#FFE9B0` / `#5B5F6E`.
- [x] Bóng Mực thân / viền / bị choáng: `#120A1A` / `#7A3CFF` / `#3A3450`.
- [x] Áo Mây / Khăn Mây: `#E8E2D0` / `#C8102E`.

### 9. Ánh sáng Môi trường thích ứng
- [x] Cường độ ánh sáng môi trường tăng dần theo tiến độ thắp đèn:
  $$\text{Intensity} = 0.15 + 0.55 \times \frac{\text{Đèn đã sáng}}{\text{Tổng số đèn}}$$
