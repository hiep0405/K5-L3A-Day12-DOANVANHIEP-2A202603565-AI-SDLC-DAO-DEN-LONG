# Đánh giá & Rút kinh nghiệm (Retro Phase 1)

## 1. Những gì đã hoàn thành
- [x] Triển khai thành công `game.contract.json` và chế độ headless `run_headless.py` tuân thủ 100% Test Contract v1.0.
- [x] Đạt tính tất định (*deterministic*): Cùng seed cho ra output JSONL giống hệt nhau.
- [x] Xây dựng game 3D trực quan bằng Three.js (chạy offline với `web/js/three.min.js`), có đầy đủ nhân vật Mây đội nón lá, 5 Đèn Lồng Lớn, đom đóm phát sáng, Bóng Mực và hiệu ứng Tỏa Sáng (Pulse).
- [x] Tạo bộ âm thanh tương tác thuật toán (Web Audio API) không cần tải asset ngoài, an toàn bản quyền 100%.
- [x] Viết bộ kiểm thử tự động `tests/test_headless.py` đạt 6/6 test cases.

## 2. Lỗi và Khó khăn gặp phải với AI
- **Lỗi bộ lọc bản quyền (Content Safety Filter):** Khi sinh file LICENSE/CREDITS có chứa đoạn text mẫu bản quyền phổ biến, bộ lọc an toàn đã chặn phản hồi.
  - *Cách khắc phục:* Viết lại phần ghi nhận tác quyền bằng ngôn từ ngắn gọn, độc lập, tập trung vào bản chất đóng góp và sử dụng mã nguồn.
- **Đảm bảo đúng Exit Code:** Test contract yêu cầu mã thoát 2 khi file scenario/inputs lỗi cú pháp và 0 khi thành công. Cần ép AI xử lý rõ ràng khối `try...except ValueError` và `os.path.exists` trước khi chạy mô phỏng.

## 3. Bài học cho các Phase tiếp theo
- Giữ các hàm logic độc lập, dễ mở rộng khi Ticket-02 (Phase 2) có thể bổ sung quái vật mới hoặc chướng ngại vật trên đảo.
