# Changelog — Đảo Đèn Lồng (Island of Lanterns)

Tất cả các thay đổi đáng chú ý của dự án qua từng phase và contract version được ghi nhận tại đây.

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
