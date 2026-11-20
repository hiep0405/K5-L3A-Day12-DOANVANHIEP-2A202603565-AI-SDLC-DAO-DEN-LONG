# Đánh giá & Rút kinh nghiệm (Retro Phase 3)

Dự án: **Đảo Đèn Lồng** — Phase 3 (Ticket-03 "Đèn cạn dầu")
Sinh viên: **Đoàn Văn Hiệp** — MSSV: **2A202603565** — Lớp: **K5-L3A**

## 1. Những gì đã hoàn thành trong Phase 3
- [x] Nâng cấp Test Contract lên **v1.2** với các tham số chuẩn hóa: `fuel_max = 100`, `fuel_decay_per_s = 1.0`, `fuel_per_mote = 10`, `drain_per_s = 5`, `low_fuel_threshold = 30`, `relight_cost = 5`, `win_ratio = 0.6`.
- [x] Hiện thực cơ chế hao hụt nhiên liệu tự nhiên và sự kiện `lantern_out` khi hết dầu (`reason: "fuel_empty"`).
- [x] Cơ chế châm dầu (`refuel`) cho đèn đang sáng và thắp lại với 5 đom đóm cho đèn đã từng sáng (`ever_lit: True`).
- [x] Mở rộng trạng thái Bóng Mực: thêm trạng thái `drain` khi tiếp cận đèn yếu ($< 30$ fuel), hút 5 fuel/giây và phát sự kiện `fuel_drain`. Tỏa Sáng trúng Bóng Mực đang drain thưởng +15 điểm.
- [x] Vùng an toàn 6m chỉ có hiệu lực khi `fuel >= 30.0`. Khi `fuel < 30.0`, đèn mất vùng an toàn và nhấp nháy báo động ở tần số 1 Hz.
- [x] Thay thế điều kiện thắng: bỏ thắng sớm `all_lit`, chuyển thành sống sót tới bình minh (hết giờ) và đạt $\ge 60\%$ đèn sáng (`reason: "dawn_survived"`).
- [x] Sức chứa đom đóm động (Dynamic carry capacity): bắt đầu từ 10, tăng +2 mỗi lần thắp đèn thành công (lần đầu hoặc thắp lại), tối đa 20 đom đóm.
- [x] Chế độ hỗ trợ người mù màu (Colorblind mode) với phím tắt nhanh `C` và bảng điều khiển trong Cài đặt.
- [x] Đạt **22/22 test cases tự động** (100% pass), tốc độ chạy 22 test trong ~0.27 giây.

---

## 2. Phân tích lỗi và Xử lý Hồi quy (Regression Analysis)
- **Xung đột điều kiện kết thúc sớm giữa Phase 1 & 3:**
  - *Hiện tượng:* `test_lantern_deposit_and_win` trong `test_headless.py` kiểm tra `game_over` ngay khi thắp hết đèn.
  - *Nguyên nhân:* Ticket-03 [THAY THẾ] luật "thắp hết đèn thì thắng ngay", yêu cầu phải sống sót tới hết giờ mới thắng.
  - *Cách xử lý:* Tách thành 2 bài test rõ ràng: `test_lantern_deposit_and_light` (kiểm tra nạp 10 đom đóm và thắp đèn thành công) và `test_dawn_survival_victory` (kiểm tra hết giờ với $\ge 60\%$ đèn sáng đạt chiến thắng với `dawn_survived`).
- **Xung đột Darkness Deadlock trong kịch bản test chuyển động:**
  - *Hiện tượng:* `test_dash_mechanic` và `test_jump_pad_launch` của Phase 2 bị fail do mô phỏng dừng ngay ở tick 1 với lý do `darkness`.
  - *Nguyên nhân:* Hai bài test này khởi tạo `carried: 0`, `random_motes: False` và không có đèn sáng nào, trùng với điều kiện bế tắc tuyệt đối mới của Phase 3.
  - *Cách xử lý:* Cập nhật kịch bản test với `carried: 1` để người chơi không bị coi là bế tắc, cho phép test các cơ chế vật lý (Lướt và Bục nhảy) chạy trọn vẹn.

---

## 3. Bài học kinh nghiệm
- Khi tiếp nhận Change Request (CR) có đánh dấu [THAY THẾ], việc cập nhật ADR (Architecture Decision Record) và CHANGELOG trước khi sửa mã giúp định hình toàn bộ luồng dữ liệu, tránh bị sót các ràng buộc tinh vi như `new_capacity` hay điểm thưởng bình minh.
