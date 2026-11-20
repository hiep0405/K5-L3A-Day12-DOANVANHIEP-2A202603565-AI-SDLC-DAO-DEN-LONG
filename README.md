# Đảo Đèn Lồng (Island of Lanterns) — Day 12 AI SDLC

> **Học viên:** Đoàn Văn Hiệp — **MSSV:** 2A202603565 — **Lớp:** K5-L3A  
> **Dự án:** Game 3D Đảo Đèn Lồng qua 4 Phase phát triển bằng quy trình AI SDLC.  
> **Tag:** `phase-3` · **Test Contract:** `v1.2`

---

## 1. Hướng dẫn Cài đặt & Chạy Game (Tối đa 3 lệnh)

Game được thiết kế không phụ thuộc thư viện C/GPU ngoài, chỉ dùng Python Standard Library và Three.js offline:

```bash
# Lệnh 1: Cài đặt (Không cần cài thêm gói ngoài)
python -m pip install -r requirements.txt

# Lệnh 2: Chơi game 3D trực quan trên trình duyệt (Cơ chế Đèn cạn dầu & Sống sót tới bình minh)
python run_game.py

# Lệnh 3: Chạy toàn bộ 22 bài kiểm thử tự động Test Contract v1.2
python -m unittest discover -s tests -p "test_*.py"
```

### Chạy chế độ Headless (Test Contract v1.2)
```bash
# Chạy Đêm 1 (Đảo Bến - 240s)
python run_headless.py --seed 42 --night 1 --ticks 1200 --out output_night1.jsonl --snapshot-every 10

# Chạy Đêm 2 (Đảo Cau - 270s)
python run_headless.py --seed 42 --night 2 --ticks 1200 --out output_night2.jsonl --snapshot-every 10

# Chạy Đêm 3 (Đảo Chuông - 300s)
python run_headless.py --seed 42 --night 3 --ticks 1200 --out output_night3.jsonl --snapshot-every 10
```

---

## 2. Giới thiệu Game & Điều khiển (Phase 3 — "Đèn Cạn Dầu")

### Cơ chế Cốt lõi mới của Phase 3 (Ticket-03 & Contract v1.2):
1. **Nhiên liệu Đèn (Lantern Fuel):**
   - Đèn sau khi thắp có `fuel = 100`, tự hao hụt $1.0$ đơn vị/giây.
   - Hết dầu (`fuel <= 0`) $\to$ đèn tắt, phát sự kiện `lantern_out` (`reason: "fuel_empty"`).
   - **Thắp lại:** Đèn đã từng sáng (`ever_lit: True`) chỉ cần **5 đom đóm** để thắp lại (thay vì 10).
   - **Châm dầu:** Tương tác với đèn đang sáng ($< 100$ fuel) để nạp thêm dầu (+10 fuel/đom đóm), phát sự kiện `refuel`.
2. **Bóng Mực hút dầu (`drain`):**
   - Vùng an toàn 6m chỉ có hiệu lực khi đèn có `fuel >= 30.0`. Khi `fuel < 30`, vùng an toàn mất, đèn và thanh dầu nhấp nháy ở tần số 1 Hz.
   - Bóng Mực `wander` tự động tìm đèn yếu ($< 30$ fuel) và chuyển sang trạng thái `drain` khi cách đèn $\le 2$m, hút $5.0$ fuel/giây.
   - Tỏa Sáng trúng Bóng Mực đang hút dầu được thưởng **+15 điểm**.
3. **Mục tiêu mới: Sống sót tới bình minh (Dawn Survival):**
   - Không còn thắng sớm khi thắp hết đèn.
   - Thắng khi hết giờ Đêm VÀ tại thời điểm đó có ít nhất **60% số đèn đang sáng** (Đêm 1: $\ge 3/5$, Đêm 2: $\ge 4/6$, Đêm 3: $\ge 5/7$), lý do: `dawn_survived`.
4. **Sức chứa Đom Đóm Động (Dynamic Capacity):**
   - Bắt đầu với sức chứa 10 đom đóm. Mỗi lần thắp sáng thành công một đèn (lần đầu hoặc thắp lại) tăng vĩnh viễn +2 sức chứa, tối đa 20 đom đóm.
5. **Chế độ Hỗ trợ Người Mù Màu (Colorblind Mode):**
   - Phím tắt nhanh `C` hoặc tùy chọn trong Cài đặt: viền Bóng Mực đổi sang xanh cyan `#00B3FF`, mắt trắng dạ quang, icon cảnh báo `⚠` trên đầu đèn yếu.

### Phím điều khiển:
* **W, A, S, D / Phím mũi tên:** Di chuyển Mây.
* **Space:** Nhảy (vận tốc $7.0 m/s$, trọng lực $-20 m/s^2$).
* **Shift:** **Lướt (Dash)** — tốc độ $14 m/s$ trong $0.2s$, hồi chiêu $1.5s$.
* **E:** Nạp đom đóm thắp đèn / Châm dầu cho đèn đang sáng.
* **F / Chuột trái:** **Tỏa Sáng (Pulse)** — tốn 3 đom đóm, hồi chiêu $3.0s$. Choáng Bóng Mực trong $5m$ suốt 120 tick và đẩy lùi $4m$.
* **C:** Bật / Tắt nhanh Chế độ hỗ trợ người mù màu (Colorblind mode).
* **P / Escape:** Tạm dừng game (Pause menu).
* **Kéo chuột:** Xoay tự do góc nhìn camera 3D.

---

## 3. Cách tính điểm (Chuẩn hóa Contract v1.2)

* **Nạp đom đóm vào đèn (thắp mới hoặc châm dầu):** $+5$ điểm / đom đóm.
* **Thắp sáng 1 Đèn Lồng Lớn lần đầu:** $+100$ điểm.
* **Thắp lại 1 ngọn đèn đã tắt:** $+40$ điểm.
* **Làm choáng 1 Bóng Mực bình thường:** $+5$ điểm.
* **Làm choáng 1 Bóng Mực đang hút dầu (`drain`):** $+15$ điểm.
* **Thưởng bình minh khi chiến thắng:**
  $$\text{Thưởng Bình Minh} = \text{Số Ngọn Lửa} \times 50 + \sum_{\text{đèn đang sáng}} (50 + \lfloor \text{fuel} \rfloor)$$

---

## 4. Sáng tạo của tôi (My Creative Additions)

1. **Thanh nhiên liệu 3D Billboard & Hiệu ứng Nhấp nháy 1 Hz:** Thanh dầu 3D xoay hướng theo góc nhìn camera, đổi màu từ xanh sang cam-đỏ và nhấp nháy cảnh báo trực quan khi `fuel < 30`.
2. **Tia năng lượng hút dầu (Drain Beam):** Thể hiện trực quan dòng năng lượng sương đen khi Bóng Mực đứng hút dầu của ngọn đèn lồng.
3. **Âm thanh cạn dầu thuật toán (Burnout procedural audio):** Tiếng sương đen dập tắt ngọn đèn lồng tạo bằng Web Audio API không tốn tài nguyên.

---

## 5. Cấu trúc Thư mục

```text
├── game.contract.json         # Test Contract v1.2
├── AGENTS.md                  # Harness AI Agent v1.2
├── CHANGELOG.md               # Nhật ký thay đổi và breaking changes
├── run_headless.py            # Entry point chạy Headless 60 tick/s
├── run_game.py                # Entry point mở game 3D 3 Đêm
├── requirements.txt           # 0 external packages
├── CREDITS.md                 # Ghi nhận tác quyền
├── src/
│   └── core/
│       └── engine.py          # Lõi mô phỏng toán học tất định (Contract v1.2)
├── web/
│   ├── index.html             # Game 3D Three.js, thanh dầu 3D, Colorblind mode
│   └── js/
│       └── three.min.js       # Thư viện Three.js offline
├── tests/
│   ├── test_headless.py       # Bộ test regression Contract v1.2
│   ├── test_phase2.py         # Bộ test cơ chế 3 Đêm & vật lý
│   └── test_phase3.py         # Bộ test chuyên sâu cho Ticket-03 "Đèn cạn dầu"
└── docs/
    ├── notes/
    │   ├── adr_phase3.md      # Quyết định kiến trúc cơ chế Đèn cạn dầu
    │   ├── token_log.md       # Nhật ký token
    │   └── retro.md           # Đánh giá rút kinh nghiệm Phase 3
    └── proof/
        └── phase-3/           # Dữ liệu nghiệm thu & chứng minh tất định
            ├── SUMMARY.md
            ├── night1.jsonl
            ├── night2.jsonl
            └── night3.jsonl
```
