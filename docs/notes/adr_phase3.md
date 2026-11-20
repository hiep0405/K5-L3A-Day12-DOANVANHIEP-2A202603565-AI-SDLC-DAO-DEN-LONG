# ADR-003: Cơ chế Đèn Cạn Dầu & Sống Sót Tới Bình Minh (Contract v1.2)

## 1. Bối cảnh (Context)
Trong Phase 1 và Phase 2, điều kiện chiến thắng là thắp sáng toàn bộ Đèn Lồng Lớn trên đảo. Tuy nhiên, dữ liệu playtest thực tế cho thấy những người chơi có kỹ năng có thể hoàn thành việc thắp hết đèn chỉ trong vòng 2 phút đầu tiên. Sau khi đèn đã thắp, đảo trở nên hoàn toàn an toàn (do vùng an toàn 6m vĩnh viễn), loại bỏ áp lực sinh tồn ở nửa sau của Đêm.
Khách hàng và Lead Designer đã gửi Ticket-03 (Change Request "Đèn cạn dầu") nhằm tái cấu trúc mục tiêu cốt lõi: từ "thắp hết đèn để thắng ngay" chuyển thành "bảo vệ ánh sáng hòn đảo sống sót tới bình minh".

---

## 2. Quyết định Thiết kế (Decisions)

### D-01: Hệ thống Nhiên liệu Đèn (Lantern Fuel System)
- Đèn sau khi thắp (hoặc thắp lại) bắt đầu với `fuel = 100.0`.
- Nhiên liệu tự nhiên hao hụt với tốc độ chuẩn 1.0 đơn vị/giây (tương ứng 1/60 đơn vị mỗi tick ở tần số 60 FPS).
- Khi `fuel <= 0`, đèn tắt hoàn toàn (`lantern_out`, `reason: "fuel_empty"`, `deposited = 0`). Đèn ghi nhớ cờ `ever_lit = True`.
- **Thắp lại (Relighting):** Đèn đã từng sáng (`ever_lit = True`) chỉ yêu cầu **5 đom đóm** để thắp lại (thay vì 10 đom đóm lần đầu). Thắp lại thưởng +40 điểm và tăng sức chứa túi.
- **Châm dầu (Refueling):** Người chơi có thể tương tác với đèn đang sáng (`fuel < 100`) để châm thêm dầu: tiêu tốn `used = min(carried, ceil((100 - fuel) / 10))` đom đóm, phục hồi `10 * used` nhiên liệu, thưởng +5 điểm / đom đóm. Đèn đầy dầu (100) không tiếp nhận thêm đom đóm.

### D-02: Hành vi Bóng Mực Hút Dầu (Shade Drain Mechanic)
- **Vùng an toàn có điều kiện:** Đèn chỉ tạo vùng an toàn 6m khi `fuel >= 30.0`. Khi `fuel < 30.0`, vùng an toàn bị vô hiệu hóa hoàn toàn, đèn và thanh dầu nhấp nháy báo động ở tần số 1 Hz.
- **Hút dầu:** Bóng Mực ở trạng thái `wander` ưu tiên tiếp cận ngọn đèn yếu (`fuel < 30`) gần nhất. Khi vào cự ly $\le 2$m (XZ), Bóng Mực chuyển sang trạng thái mới `drain`, đứng yên và rút 5 đơn vị dầu/giây (cộng dồn nếu nhiều con).
- **Chuyển trạng thái từ drain:**
  - Nếu Mây tiến vào bán kính 6m $\to$ chuyển sang `chase`.
  - Nếu trúng Tỏa Sáng (Pulse) $\to$ chuyển sang `stunned`, thưởng **+15 điểm** (thay vì +5 điểm) cho hành động bảo vệ đèn kịp thời.
  - Nếu đèn tắt hoặc được châm dầu lên $\ge 30 \to$ chuyển về `wander`.

### D-03: Điều kiện Thắng/Thua Mới — Sống sót tới bình minh
- **Hủy bỏ thắng sớm:** Game không còn kết thúc ngay khi thắp hết đèn. Toàn bộ đêm diễn ra cho tới khi bộ đếm thời gian về 0 (bình minh).
- **Điều kiện thắng:** Khi hết thời gian Đêm, số đèn đang sáng phải đạt ít nhất 60% tổng số đèn trên đảo:
  - Đêm 1 (5 đèn): Cần $\ge 3$ đèn sáng.
  - Đêm 2 (6 đèn): Cần $\ge 4$ đèn sáng.
  - Đêm 3 (7 đèn): Cần $\ge 5$ đèn sáng.
  - Lý do kết thúc: `dawn_survived`.
- **Điều kiện thua:**
  - Mất hết Ngọn Lửa (`reason: "no_flames"`).
  - Hết giờ nhưng không đủ 60% số đèn sáng (`reason: "dawn_insufficient_light"`).
  - Bế tắc tuyệt đối (`reason: "darkness"`): Toàn bộ đèn đều tắt, người chơi có 0 đom đóm, và không còn đom đóm nào trên bản đồ.

### D-04: Sức chứa Đom Đóm Động (Dynamic Carry Capacity)
- Khởi đầu mỗi Đêm với sức chứa 10 đom đóm.
- Mỗi lần thắp sáng thành công một ngọn đèn (lần đầu hoặc thắp lại): sức chứa tối đa tăng vĩnh viễn thêm +2 cho tới hết Đêm đó (tối đa 20 đom đóm).

### D-05: Khả năng tiếp cận — Chế độ hỗ trợ người mù màu (Colorblind Mode)
- Cung cấp tùy chọn "Bảng màu dễ phân biệt" trong Cài đặt và phím tắt nhanh `C`.
- Chuyển màu Bóng Mực từ tím đen sang xanh lam đậm viền xanh sáng cyan (`#00B3FF`) với mắt trắng dạ quang.
- Hiển thị icon cảnh báo `⚠` nổi bật trên đầu ngọn đèn khi `fuel < 30`.

---

## 3. Hậu quả & Đánh giá (Consequences)
- **Tác động:** Tạo nhịp độ chơi dồn dập, đòi hỏi chiến thuật di chuyển liên tục giữa các ngọn đèn thay vì chỉ thắp xong một lượt rồi đứng yên.
- **Tính tương thích:** Đảm bảo 100% tuân thủ Test Contract v1.2, các trường dữ liệu JSONL mới (`refuel`, `lantern_out`, `fuel_drain`, `new_capacity`, `dawn_survived`) đều được chuẩn hóa và kiểm thử nghiêm ngặt.
