# Báo Cáo Hồi Cứu & Đánh Giá Toàn Diện 4 Phase (Retro v1.0.0)

**Dự án:** Đảo Đèn Lồng (Island of Lanterns) — Day 12 AI SDLC  
**Học viên:** Đoàn Văn Hiệp — **MSSV:** 2A202603565 — **Lớp:** K5-L3A  
**Phiên bản phát hành:** `v1.0.0` (Contract v1.3)

---

## 1. Tổng hợp Đánh giá (Evaluation) qua 4 Phase

| Phase | Mục tiêu chính | Trạng thái | Điểm nổi bật & Thách thức đã vượt qua |
|---|---|---|---|
| **Phase 1 (Contract v1.0)** | PRD-0 Đảo Bến, 5 đèn lồng, di chuyển, nhặt đom đóm, Tỏa Sáng, quái Bóng Mực, web 3D Three.js và headless engine. | **Hoàn thành** | Xây dựng lõi mô phỏng 60 tick/s độc lập không phụ thuộc thư viện C/GPU ngoài. Xác định tính tất định 100% bằng seed. |
| **Phase 2 (Contract v1.1)** | Ticket-02 mở rộng 3 Đêm, chuẩn hóa thông số, cơ chế Lướt, Gió Lạc, Bùa Gió, Bục Nhảy và phạt rơi vực. | **Hoàn thành** | Xử lý xung đột hằng số chuẩn hóa (`lantern_cost`: 5 $\to$ 10, `pulse_cost`: 1 $\to$ 3) bằng phân tích hồi quy, giữ vững 14/14 tests xanh. |
| **Phase 3 (Contract v1.2)** | Ticket-03 Change Request "Đèn cạn dầu", Bóng Mực hút dầu, chuyển từ thắng sớm sang sống sót tới bình minh ($\ge 60\%$ đèn sáng). | **Hoàn thành** | Lập ADR-003 phân tích thay đổi phá vỡ tương thích, bổ sung cơ chế dầu, bảo vệ đèn thưởng +15 điểm, sức chứa động (10 $\to$ 20). |
| **Phase 4 (Contract v1.3)** | Ticket-04 Phát hành v1.0.0: Benchmark đo FPS, Soak test 10 đêm, Bảng xếp hạng cục bộ, Tiếp cận (Accessibility), Đóng gói README. | **Hoàn thành** | Đạt `avg_fps: 64.2` ($\ge 60$), `p1_low_fps: 57.5` ($\ge 30$), `load_ms: 23.1 ms` ($\le 10000$), Soak test 10 đêm không crash, không rò rỉ RAM (2.9s). |

---

## 2. Làm việc với AI: Điều gì Hiệu quả và Không Hiệu quả

### Những gì hiệu quả vượt trội (What Worked Well)
1. **Chuyển dịch Test Contract thành Code & Test Cases tức thì:** AI chuyển đổi tài liệu PRD dạng văn bản sang cấu trúc dữ liệu JSON Schema (`game.contract.json`) và sinh ra các bộ unit test cực kỳ nhanh chóng và bao phủ toàn diện.
2. **Kế thừa kiến trúc (Architecture Continuity):** AI duy trì rất tốt cấu trúc 12 bước tick của simulation loop trong `src/core/engine.py`, giúp bổ sung tính năng mới (Bùa Gió, Bục Nhảy, Dầu đèn, Trạng thái `drain`) mà không làm gãy vỡ các logic cũ.
3. **Phát triển Song song (Parallel Development):** Khả năng đồng thời phát triển WebGL Three.js client và Python Headless Engine với cùng một tập logic toán học, bảo đảm hành vi trong game trực quan khớp hoàn toàn với bài đo headless.

### Những gì không hiệu quả (What Didn't Work Well)
1. **Thiếu trực giác về các kịch bản biên trong test cũ:** Khi đưa vào luật mới "Darkness Deadlock" ở Phase 3, AI ban đầu áp dụng điều kiện bế tắc ngay cả với các kịch bản test chuyển động của Phase 2 (nơi tác giả cố ý để `carried: 0` và không có đèn sáng để test nhảy thuần túy). Cần sự can thiệp phân tích kỹ của con người để gỡ bỏ xung đột.
2. **Tự động thêm văn bản bản quyền bên ngoài:** AI có xu hướng trích xuất nguyên văn giấy phép mã nguồn mở của bên thứ ba, dễ kích hoạt bộ lọc bản quyền tự động. Cần chủ động hướng dẫn AI viết tóm tắt ngắn gọn nguyên bản.

---

## 3. Những lần AI Sai và Cách Phát hiện / Sửa chữa

1. **Lỗi `__pycache__` trong git commit (Phase 1):**
   - *Phát hiện:* Lệnh `git status` trước khi gắn tag hiển thị các tệp bytecode `.pyc`.
   - *Xử lý:* Tạo `.gitignore` chuẩn cho Python và thực hiện `git rm --cached` trước khi commit.
2. **Xung đột hằng số Phase 2:**
   - *Phát hiện:* Sau khi chuẩn hóa `lantern_cost = 10` và `pulse_cost = 3`, 2 bài test cũ bị fail do chỉ cấp 5 và 1 đom đóm.
   - *Xử lý:* Đọc lại checklist so sánh giữa v1.0 và v1.1, cập nhật dữ liệu test scenario và ghi chú rõ ràng vào CHANGELOG.
3. **Timer resolution trên Windows trong Benchmark (Phase 4):**
   - *Phát hiện:* Khi chạy đo FPS với `time.sleep` thông thường trên Windows, độ phân giải timer mặc định là 15.6ms khiến FPS bị ghìm ở ~64 FPS.
   - *Xử lý:* Tích hợp lệnh gọi Windows Multimedia API `timeBeginPeriod(1)` qua `ctypes` để đạt độ phân giải 1ms, bảo đảm đo đạc mượt mà và chính xác.

---

## 4. Đánh giá Harness: Cái gì Giúp Nhiều Nhất?

1. **`AGENTS.md` (Hiệu quả nhất - 10/10):**
   - Đóng vai trò kim chỉ nam bất biến cho AI qua từng phase. Quy định rõ thứ tự 12 bước trong 1 tick, danh sách tên trạng thái của Bóng Mực, và các lệnh bắt buộc. Nhờ đó, AI không bao giờ tự ý đổi tên trường JSONL hay đổi cấu trúc thư mục.
2. **Test Contract (`game.contract.json` - 9.5/10):**
   - Cung cấp "Single Source of Truth" cho toàn bộ hằng số game. Khi hằng số thay đổi ở Phase 2 & 3, chỉ cần đọc contract là cả engine, test và tài liệu đều đồng bộ hoàn hảo.
3. **Bộ kiểm thử tự động `unittest` (9.5/10):**
   - Chạy 27 bài test chỉ trong 6 giây, cung cấp phản hồi tức thì mỗi khi có dòng code nào sửa đổi (Fast Feedback Loop).

---

## 5. Tổng kết Token & Chi phí AI

- **Phase 1:** ~21,500 tokens (~$0.03)
- **Phase 2:** ~30,500 tokens (~$0.05)
- **Phase 3:** ~37,200 tokens (~$0.06)
- **Phase 4:** ~32,000 tokens (~$0.05)
- **Tổng toàn bộ dự án:** **~121,200 tokens** (Chi phí ước tính: **~$0.19**)

### Chiến lược tiết kiệm token đã áp dụng:
1. **Gộp lệnh (Batching):** Đọc nhiều tệp và thực thi nhiều lệnh phụ thuộc bằng `&&` trong cùng 1 turn, tránh lãng phí context gửi đi gửi lại.
2. **Phân tích trước khi sinh code:** Đọc kỹ ticket và xác định diff cụ thể trước khi viết code, hạn chế tối đa các lượt "thử rồi sai" (trial and error).
3. **Tái sử dụng module:** Kế thừa `src/core/engine.py` xuyên suốt 4 phase thay vì viết lại từ đầu.

---

## 6. Nếu Làm Lại từ Đầu, Sẽ Thay Đổi Điều Gì?
1. **Thiết kế State Machine của thực thể theo hướng mở ngay từ đầu:** Nếu từ Phase 1 đã dùng Enum hoặc State Pattern tường minh cho Bóng Mực (`WANDER`, `CHASE`, `DRAIN`), việc mở rộng sang Phase 3 sẽ gọn gàng hơn nữa.
2. **Tách biệt Scenario Tester và Gameplay Simulator:** Thiết lập một cờ `is_testing_mode` riêng biệt để các bài test kiểm tra chuyển động cô lập không bị vướng vào các cơ chế game-over toàn cục như `darkness`.
