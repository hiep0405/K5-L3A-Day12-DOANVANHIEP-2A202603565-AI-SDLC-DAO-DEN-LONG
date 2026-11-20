# Đánh giá & Rút kinh nghiệm (Retro Phase 2)

Dự án: **Đảo Đèn Lồng** — Phase 2 (Ticket-02)
Sinh viên: **Đoàn Văn Hiệp** — MSSV: **2A202603565**

## 1. Những gì đã hoàn thành
- [x] Mở rộng hoàn chỉnh mô phỏng sang **3 Đêm** (Đêm 1: Đảo Bến, Đêm 2: Đảo Cau 2 đảo nối cầu tre, Đêm 3: Đảo Chuông 3 tầng vách đứng và bục nhảy).
- [x] Nâng cấp Test Contract lên **v1.1** với đầy đủ các khóa snapshot (`wind`, `vel`, `grounded`, `dash_cd_s`, `charms`, `drifters`).
- [x] Hiện thực cơ chế Lướt (Dash 14 m/s), Bùa Gió (tốc độ 7.2 m/s, không hồi chiêu Lướt), Gió Lạc (cướp đom đóm & rơi đồ khi bị Tỏa Sáng), và Bục Nhảy (Jump Pads).
- [x] Cơ chế phạt rơi khỏi đảo (Y < -10) trừ 1 ngọn lửa, rơi hết đom đóm và hồi sinh sau 60 tick.
- [x] Giao diện game 3D cập nhật bảng màu chuẩn của Ticket-02, thanh đom đóm 10 ô, hệ thống 3 Đêm chiến dịch kèm lời dẫn Ông Đăng và màn hình Bình Minh khi chiến thắng.
- [x] Đạt **14/14 test cases tự động**, chạy 21.600 tick trong chưa đầy 1 giây (vượt xa chỉ tiêu $\le 30$s).

## 2. Phân tích lỗi và Xử lý Hồi quy (Regression Analysis)
- **Xung đột hằng số chuẩn hóa giữa Phase 1 và Phase 2:**
  - *Hiện tượng:* Khi chạy lại test Phase 1, 2 test case (`test_lantern_deposit_and_win` và `test_pulse_stun_shade`) bị fail.
  - *Nguyên nhân:* Ticket-02 đã chuẩn hóa `lantern_cost = 10` (trước là 5) và `pulse_cost = 3` (trước là 1). Test cũ tạo `carried: 5` và `carried: 2` nên không đủ điều kiện kích hoạt.
  - *Cách xử lý:* Cập nhật giá trị test tương ứng kèm ghi chú lý do rõ ràng theo đúng quy định tại `CHECKPOINTS.md`.

## 3. Bài học kinh nghiệm
- Việc tuân thủ nghiêm ngặt thứ tự 12 bước trong 1 tick giúp các hệ thống tương tác phức tạp (Bùa Gió $\rightarrow$ Di chuyển $\rightarrow$ Nhặt đồ $\rightarrow$ Quái chạm $\rightarrow$ Rơi đồ) không bao giờ bị tranh chấp hoặc lỗi thứ tự ưu tiên.
