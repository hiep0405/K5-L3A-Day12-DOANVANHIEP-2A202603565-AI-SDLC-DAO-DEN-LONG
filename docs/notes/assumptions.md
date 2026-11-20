# Giả định thiết kế Phase 1 (Assumptions)

## 1. Không gian và Địa hình
- Đảo Bến có dạng hình tròn, tâm tại $(0, 0, 0)$, bán kính danh nghĩa là $50m$.
- Người chơi Mây xuất phát tại tâm $(0, 0, 0)$ ở $Y = 0$.
- Trong Phase 1, `fall_enabled = false`, Mây di chuyển tự do trên mặt phẳng đảo $XZ$.

## 2. Đèn Lồng Lớn (5 đèn L1 đến L5)
- 5 Đèn Lồng Lớn được bố trí đều theo vòng tròn bán kính $R = 25m$ quanh tâm:
  - $L_1$: $(0.0, 0.0, 25.0)$
  - $L_2$: $(23.776, 0.0, 7.725)$
  - $L_3$: $(14.695, 0.0, -20.225)$
  - $L_4$: $(-14.695, 0.0, -20.225)$
  - $L_5$: $(-23.776, 0.0, 7.725)$
- Mỗi đèn cần $5$ đom đóm (`lantern_cost: 5`) để thắp sáng hoàn toàn.
- `safe_radius`: $4.0m$. Bóng Mực sợ ánh sáng của các ngọn đèn, do đó không thể tiến vào bán kính $\le 4.0m$ quanh các Đèn Lồng Lớn (vị trí Bóng Mực sẽ bị chặn lại ở rìa bán kính an toàn).

## 3. Đom đóm (Motes)
- Mặc định khởi tạo 25 đom đóm rải rác trên đảo (bán kính từ $5m$ đến $45m$).
- Bán kính nhặt: $1.5m$. Khi Mây trong phạm vi $1.5m$ và túi chưa đầy (`carried < 10`), đom đóm tự động được thu gom.
- Mỗi đom đóm thu gom mang lại $10$ điểm.

## 4. Bóng Mực (Shades)
- Mặc định sinh 3 Bóng Mực ở các hướng cách tâm $30m$.
- Tốc độ di chuyển: $3.5 m/s$, luôn hướng thẳng về vị trí chân của Mây.
- Bán kính gây sát thương: $1.0m$.
- Khi Mây bị trúng đòn: mất $1$ ngọn lửa (`flames -= 1`), rơi $50\%$ số đom đóm đang mang (`dropped = floor(carried * 0.5)`), và nhận trạng thái bất tử tạm thời trong $1.5$ giây (`invuln_s`).

## 5. Tỏa sáng (Pulse)
- Tốn $1$ đom đóm đang mang (`pulse_cost: 1`), hồi chiêu $2.0$ giây.
- Bán kính tác dụng: $5.0m$.
- Mọi Bóng Mực trong bán kính $5.0m$ bị đẩy lùi $2.0m$ theo hướng ra xa Mây và bị choáng (stun) trong $3.0$ giây.
- Mỗi Bóng Mực bị stun mang lại $20$ điểm.

## 6. Điều kiện Kết thúc & Tính điểm
- **Thắng:** Thắp sáng toàn bộ 5 đèn lồng.
  - Điểm thưởng thắng = $\lfloor \text{time\_left\_s} \rfloor \times 1 + \text{flames} \times 50$.
- **Thua:** Mất hết máu (`flames <= 0`, reason: `no_flames`) hoặc hết thời gian $300$ giây (reason: `dawn`).
