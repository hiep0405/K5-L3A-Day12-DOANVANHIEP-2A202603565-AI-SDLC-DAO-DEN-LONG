# Nhật ký sử dụng AI & Ước tính Token (Phase 1 & 2)

Dự án: **Đảo Đèn Lồng**
Sinh viên: **Đoàn Văn Hiệp** — MSSV: **2A202603565**

## 1. Ước tính Token & Chi phí

### Phase 1:
- **Tokens Prompt:** ~15,000 | **Tokens Completion:** ~6,500
- **Chi phí ước tính:** ~$0.03

### Phase 2 (Ticket-02 — "Ba hòn đảo"):
- **Tokens Prompt:** ~22,000 | **Tokens Completion:** ~8,500
- **Chi phí ước tính:** ~$0.05
- **Tổng cộng 2 Phase:** ~52,000 tokens (~$0.08)

## 2. Chiến lược Tối ưu hóa Token trong Phase 2
1. **Phân tích kỹ lưỡng thay đổi của Contract v1.1:** Xác định rõ sự khác biệt giữa v1.0 và v1.1 (thêm mảng bắt buộc `drifters`, `charms`, `motes`, cập nhật 12 bước tick, trạng thái chuẩn của Bóng Mực) trước khi viết mã.
2. **Kế thừa kiến trúc Module:** Tiếp tục mở rộng `src/core/engine.py` mà không phải viết lại từ đầu, giữ trọn vẹn khả năng hồi quy (regression) cho các test Phase 1.
3. **Phát hiện và sửa sớm xung đột hằng số:** Hằng số `lantern_cost` tăng từ 5 lên 10 và `pulse_cost` tăng từ 1 lên 3 được đối chiếu và cập nhật vào bộ test ngay lập tức, tránh các vòng lặp sửa lỗi tốn token.
