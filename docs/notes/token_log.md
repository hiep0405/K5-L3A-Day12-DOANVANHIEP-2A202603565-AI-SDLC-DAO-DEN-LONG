# Nhật ký sử dụng AI & Ước tính Token (Phase 1, 2, 3)

Dự án: **Đảo Đèn Lồng** (Day 12 AI SDLC)
Sinh viên: **Đoàn Văn Hiệp** — MSSV: **2A202603565** — Lớp: **K5-L3A**

## 1. Ước tính Token & Chi phí

### Phase 1 (PRD-0 — Đảo Bến, Contract v1.0):
- **Tokens Prompt:** ~15,000 | **Tokens Completion:** ~6,500
- **Chi phí ước tính:** ~$0.03

### Phase 2 (Ticket-02 — "Ba hòn đảo", Contract v1.1):
- **Tokens Prompt:** ~22,000 | **Tokens Completion:** ~8,500
- **Chi phí ước tính:** ~$0.05

### Phase 3 (Ticket-03 — "Đèn cạn dầu", Contract v1.2):
- **Tokens Prompt:** ~28,000 | **Tokens Completion:** ~9,200
- **Chi phí ước tính:** ~$0.06
- **Tổng cộng 3 Phase:** ~89,200 tokens (~$0.14)

---

## 2. Chiến lược Tối ưu hóa Token trong Phase 3
1. **Phân tích Change Request trước khi sửa code:** Đọc kỹ Ticket-03 để tách bạch những luật cũ bị [THAY THẾ] (thắng sớm `all_lit`, đèn đã sáng không nhận đom đóm, Bóng Mực không vào vùng an toàn) khỏi các tính năng kế thừa.
2. **Kế thừa kiến trúc Module từ Phase 1 & 2:** Giữ nguyên cấu trúc simulation loop 12 bước, mở rộng các trạng thái mới (`drain`, `fuel`, `new_capacity`, `dawn_survived`) thay vì viết lại core engine.
3. **Kiểm thử hồi quy tự động & bách phát bách trúng:** Viết 9 bài test bao quát toàn bộ luật mới trong `test_phase3.py`, đồng thời bảo đảm 14 test cũ vẫn xanh 100%.
