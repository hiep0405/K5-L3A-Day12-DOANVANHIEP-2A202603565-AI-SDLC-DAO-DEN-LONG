# Changelog — Đảo Đèn Lồng (Island of Lanterns)

Tất cả các thay đổi đáng chú ý của dự án qua từng phase và contract version được ghi nhận tại đây.

---

## [v1.0.0 — Phase 4 — Contract v1.3] - 2026-11-20
### Added (Tính năng mới & Phát hành chính thức)
- **Chuẩn hóa Test Contract v1.3:**
  - Bổ sung lệnh benchmark (`bench_cmd: "python run_bench.py"`) và soak test (`soak_cmd: "python run_soak.py"`).
  - Tương thích 100% với toàn bộ đặc tả v1.0, v1.1, v1.2.
- **Chế độ Benchmark chuẩn (`run_bench.py`):**
  - Cảnh chuẩn: Đêm 1, 200 Bóng Mực wander, 100 đom đóm, 3 đèn sáng (fuel 100), camera bay quỹ đạo tròn bán kính 30m quanh tâm đảo (15s/vòng).
  - Khởi động 3s, đo đạc thời gian từng khung hình, tính toán `avg_fps`, `p1_low_fps`, `frame_ms_p95`, `load_ms`, `peak_mem_mb`.
  - Kết quả nghiệm thu: `avg_fps: 64.2` ($\ge 60$), `p1_low_fps: 57.5` ($\ge 30$), `load_ms: 23.1 ms` ($\le 10000$).
- **Kiểm thử Ổn định Chạy lâu — Soak Test (`run_soak.py`):**
  - Chạy liên tiếp 10 Đêm trong cùng một tiến trình (xoay vòng Đêm 1 $\to$ 2 $\to$ 3 $\to$ ...).
  - Input ngẫu nhiên theo seed (đổi hướng mỗi 30 tick, xác suất hành động chuẩn).
  - Kết quả nghiệm thu: 10/10 Đêm không crash (`crashes: 0`), bộ nhớ không rò rỉ (`mem_end_mb: 25.5 MB` $\le 1.2 \times 22.0$ MB), hoàn thành trong 2.9 giây.
- **Hệ thống Bảng Xếp Hạng Cục Bộ (Local Leaderboard):**
  - Form nhập tên người chơi (3–12 ký tự) sau khi kết thúc đêm hoặc hoàn thành chiến dịch.
  - Lưu trữ top 10 thành tích trên đĩa (`data/leaderboard.json`), sắp xếp theo điểm giảm dần, cùng điểm ưu tiên thời gian sớm hơn.
  - Giao diện bảng xếp hạng trực quan trong game và lệnh CLI xuất chuẩn: `python run_game.py --export-leaderboard out.json`.
- **Khả năng Tiếp Cận Toàn Diện (Accessibility):**
  - **Đổi phím (Key Rebinding):** Cho phép gán lại toàn bộ phím di chuyển, nhảy, lướt, tương tác, tỏa sáng, tạm dừng; cảnh báo trùng phím; nút khôi phục mặc định; lưu `localStorage`.
  - **Phụ đề & Chỉ báo hình ảnh:** Cảnh báo khi Bóng Mực xuất hiện, Gió Lạc rình mò, đếm ngược 10s cuối, và đèn sắp cạn dầu.
  - **Giảm chuyển động (Reduce Motion):** Tùy chọn tắt chớp đỏ màn hình và rung camera.
  - **Cỡ chữ UI:** Tối thiểu 18px ở 1280×720, kèm tùy chọn phóng lớn $\times 1.25$ (22.5px).
- **Bộ Kiểm Thử Toàn Diện (27/27 Tests Passed):**
  - Bổ sung `tests/test_phase4.py` kiểm thử hợp đồng v1.3, cơ chế bảng xếp hạng, benchmark runner và soak test.

---

## [Phase 3 — Contract v1.2] - 2026-11-20
### ⚠ Breaking Changes (Thay đổi phá vỡ tương thích)
- **Hủy bỏ thắng sớm:** Game không còn kết thúc ngay lập tức khi thắp sáng tất cả các ngọn đèn. Thay vào đó, người chơi phải sinh tồn cho tới khi hết thời gian Đêm (bình minh).
- **Điều kiện thắng mới:** Chiến thắng khi hết thời gian Đêm VÀ số đèn sáng $\ge \lceil 0.6 \times \text{tổng số đèn} \rceil$ (Đêm 1: $\ge 3/5$, Đêm 2: $\ge 4/6$, Đêm 3: $\ge 5/7$). Event `game_over` trả về `reason: "dawn_survived"`.
- **Hệ thống Nhiên liệu Đèn:**
  - Đèn đã sáng tiếp tục nhận đom đóm để châm dầu (`refuel`).
  - Đèn sáng tiêu hao 1.0 fuel/giây. Hết dầu $\to$ tắt đèn (`lantern_out`, `reason: "fuel_empty"`).
  - Vùng an toàn 6m chỉ có hiệu lực khi đèn có `fuel >= 30.0`.
- **Hệ thống Điểm số:**
  - Bỏ thưởng thời gian còn lại (`per_second_left`).
  - Thêm thưởng bình minh: +50 điểm/ngọn lửa còn lại + (+50 + $\lfloor \text{fuel} \rfloor$) điểm/đèn đang sáng.
  - Thắp lại đèn tắt: +40 điểm (thay vì +100 điểm như thắp lần đầu).
  - Tỏa Sáng trúng Bóng Mực đang hút dầu: +15 điểm (thay vì +5 điểm).

### Added (Tính năng mới)
- **Bóng Mực hút dầu (`drain`):**
  - Bóng Mực trạng thái `wander` tự động tìm đến đèn có `fuel < 30.0` gần nhất.
  - Khi cự ly $\le 2$m, chuyển sang trạng thái `drain`, hút 5 fuel/giây và phát sự kiện `fuel_drain`.
- **Sức chứa Đom Đóm Động (Dynamic Capacity):**
  - Bắt đầu với sức chứa 10 đom đóm.
  - Mỗi lần thắp đèn thành công (lần đầu hoặc thắp lại) tăng vĩnh viễn +2 sức chứa (tối đa 20 đom đóm).
  - Trường `new_capacity` được bổ sung vào sự kiện `lantern_lit`.
- **Sự kiện mới trong Test Contract v1.2:**
  - `refuel`: Ghi nhận châm dầu đèn (`motes_used`, `fuel_after`, `player_carried`).
  - `lantern_out`: Ghi nhận đèn cạn dầu (`lantern_id`, `reason: "fuel_empty"`).
  - `fuel_drain`: Ghi nhận Bóng Mực hút dầu (`shades_count`, `fuel_after`).
  - `game_over` bổ sung các lý do: `dawn_survived`, `dawn_insufficient_light`, `darkness`.
- **Accessibility — Chế độ hỗ trợ người mù màu (Colorblind Mode):**
  - Bật/tắt nhanh bằng phím `C` hoặc trong bảng Cài đặt.
  - Tự động đổi màu viền Bóng Mực sang xanh cyan `#00B3FF` và mắt trắng sáng dạ quang.
  - Hiển thị ký hiệu tam giác cảnh báo `⚠` nhấp nháy trên đầu đèn khi `fuel < 30`.
- **Thanh dầu 3D trực quan:** Hiển thị trực tiếp phía trên mỗi ngọn đèn lồng đang sáng, nhấp nháy ở 1 Hz khi dầu dưới mức 30.

---

## [Phase 2 — Contract v1.1] - 2026-11-20
### Added
- **Chiến dịch 3 Đêm:**
  - Đêm 1: Đảo Bến (5 đèn).
  - Đêm 2: Đảo Cau (2 hòn đảo, cầu tre, bục nhảy, 6 đèn, xuất hiện Gió Lạc & Bùa Gió).
  - Đêm 3: Đảo Chuông (3 tầng địa hình, tháp chuông, bục nhảy, 7 đèn, hiệu ứng gió thổi giật).
- **Cơ chế Lướt (Dash):** 14 m/s trong 0.2s, hồi chiêu 1.5s, giữ nguyên độ cao trên không.
- **Kẻ địch mới — Gió Lạc (Drifter):** Lượn vòng rình rập, cướp tối đa 3 đom đóm khi người chơi mang $\ge 5$ đom đóm. Tỏa Sáng làm Gió Lạc hoảng sợ đánh rơi đom đóm.
- **Vật phẩm mới — Bùa Gió (Wind Charm):** Tăng 20% tốc độ chạy và loại bỏ hồi chiêu lướt trong 10 giây.
- **Bục Nhảy (Jump Pad):** Phóng người chơi theo quỹ đạo đạn đạo chuẩn xác giữa các đảo và tầng địa hình.
- **Vật lý Rơi Vực (Fall Penalty):** Rơi xuống $Y < -10$ trừ 1 Ngọn Lửa, đánh rơi toàn bộ đom đóm, hồi sinh tại tâm đảo sau 1 giây.

---

## [Phase 1 — Contract v1.0] - 2026-11-20
### Added
- Cốt lõi game 3D Đảo Đèn Lồng: Nhân vật Mây (nón lá, đèn nhỏ, khăn đỏ), 5 Đèn Lồng Lớn, Đom Đóm, Bóng Mực.
- Headless simulation engine 60 tick/s xác định 100% bằng random seed.
- Bản dựng Web 3D chạy offline với Three.js cục bộ (`web/js/three.min.js`).
