# Nhật ký sử dụng AI & Ước tính Token (Phase 1)

Dự án: **Đảo Đèn Lồng**
Sinh viên: **Đoàn Văn Hiệp** — MSSV: **2A202603565**

## 1. Ước tính Token & Chi phí Phase 1
- **Mô hình sử dụng:** Gemini 3.8 Flash (High) / Claude Sonnet trên Lab Board.
- **Tổng số Prompt gửi:** ~6 lượt.
- **Ước tính Token đầu vào (Prompt):** ~15,000 tokens.
- **Ước tính Token đầu ra (Completion):** ~6,500 tokens.
- **Chi phí ước tính:** ~$0.02 - $0.05.

## 2. Chiến lược Quản lý & Tiết kiệm Token
1. **Lập kế hoạch trước khi code:** Phân tích PRD-0 và Test Contract v1.0 kỹ lưỡng, xác định rõ các thông số `tuning` và quy ước tick trước khi cho AI viết code.
2. **Kiến trúc tách rời (Decoupled Architecture):**
   - Tách biệt hoàn toàn `src/core/engine.py` (Headless simulation) và `web/index.html` (3D visualization), giúp prompt không bị cồng kềnh khi sửa đổi logic.
3. **Batch Tool Calls:** Gộp các thao tác đọc/ghi file và kiểm thử vào cùng một lượt (turn) để tránh gửi lặp context nhiều lần.
4. **Harness ngắn gọn (`AGENTS.md`):** Giữ file quy tắc dưới 40 dòng, chỉ tập trung vào các quy ước bắt buộc của Test Contract.
