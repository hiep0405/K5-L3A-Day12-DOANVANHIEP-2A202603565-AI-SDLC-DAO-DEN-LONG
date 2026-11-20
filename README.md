# Đảo Đèn Lồng (Island of Lanterns) — Day 12 AI SDLC

> **Học viên:** Đoàn Văn Hiệp — **MSSV:** 2A202603565 — **Lớp:** K5-L3A  
> **Dự án:** Game 3D Đảo Đèn Lồng qua 4 Phase phát triển bằng quy trình AI SDLC.  
> **Tag:** `phase-2` · **Test Contract:** `v1.1`

---

## 1. Hướng dẫn Cài đặt & Chạy Game (Tối đa 3 lệnh)

Game được thiết kế không phụ thuộc thư viện C/GPU ngoài, chỉ dùng Python Standard Library và Three.js offline:

```bash
# Lệnh 1: Cài đặt (Không cần cài thêm gói ngoài)
python -m pip install -r requirements.txt

# Lệnh 2: Chơi game 3D trực quan trên trình duyệt (3 Đêm chiến dịch)
python run_game.py

# Lệnh 3: Chạy toàn bộ 14 bài kiểm thử tự động Test Contract v1.1
python -m unittest discover -s tests -p "test_*.py"
```

### Chạy chế độ Headless (Test Contract v1.1)
```bash
# Chạy Đêm 1 (Đảo Bến)
python run_headless.py --seed 42 --night 1 --ticks 600 --out output_night1.jsonl --snapshot-every 10

# Chạy Đêm 2 (Đảo Cau)
python run_headless.py --seed 42 --night 2 --ticks 600 --out output_night2.jsonl --snapshot-every 10

# Chạy Đêm 3 (Đảo Chuông)
python run_headless.py --seed 42 --night 3 --ticks 600 --out output_night3.jsonl --snapshot-every 10
```

---

## 2. Giới thiệu Game & Điều khiển (Phase 2 — Ba Hòn Đảo)

Game mở rộng thành chuỗi **3 Đêm chiến dịch liên hoàn**:
1. **Đêm 1 — Đảo Bến:** Hòn đảo tròn $R = 40m$, 5 Đèn Lồng Lớn, 20 đom đóm khởi đầu.
2. **Đêm 2 — Đảo Cau:** 2 đảo tròn nối với nhau bằng cầu tre, có Bục Nhảy (Jump Pad) phóng qua lại giữa 2 đảo, xuất hiện Gió Lạc (Drifter) và Bùa Gió. 6 Đèn Lồng Lớn.
3. **Đêm 3 — Đảo Chuông:** Đảo 3 tầng vách đứng cao $6m$, dốc leo và bục nhảy lên Tháp Chuông, gió mạnh từng cơn. 7 Đèn Lồng Lớn.

### Phím điều khiển:
* **W, A, S, D / Phím mũi tên:** Di chuyển Mây.
* **Space:** Nhảy (vận tốc $7.0 m/s$, trọng lực $-20 m/s^2$).
* **Shift:** **Lướt (Dash)** — tốc độ $14 m/s$ trong $0.2s$, hồi chiêu $1.5s$ (không tốn hồi chiêu khi có Bùa Gió).
* **E:** Nạp đom đóm vào Đèn Lồng Lớn khi đứng gần (bán kính $\le 2.0m$). Cần $10$ đom đóm để thắp sáng hoàn toàn 1 đèn.
* **F / Chuột trái:** **Tỏa Sáng (Pulse)** — tốn 3 đom đóm, hồi chiêu $3.0s$. Làm choáng Bóng Mực trong $5m$ suốt 120 tick và đẩy lùi $4m$. Khi trúng Gió Lạc đang bỏ chạy, buộc Gió Lạc nhả lại toàn bộ đom đóm đã cướp.
* **P / Escape:** Tạm dừng game (Pause menu).
* **Kéo chuột:** Xoay tự do góc nhìn camera 3D.

---

## 3. Cách tính điểm (Chuẩn hóa Phase 2)

* **Nạp 1 đom đóm vào đèn:** $+10$ điểm.
* **Thắp sáng 1 Đèn Lồng Lớn:** $+100$ điểm.
* **Làm choáng 1 Bóng Mực bằng Tỏa Sáng:** $+5$ điểm (mỗi con mỗi lần).
* **Điểm thưởng khi chiến thắng mỗi Đêm:**
  $$\text{Thưởng} = \lfloor \text{Thời gian còn lại (s)} \rfloor \times 2 + \text{Số Ngọn Lửa còn lại} \times 50$$
* **Tổng điểm trò chơi:** Tổng điểm tích lũy qua các Đêm đã chiến thắng.

---

## 4. Sáng tạo của tôi (My Creative Additions)

Theo quy định trong mục F của RUBRIC, các yếu tố sáng tạo được tích hợp trọn vẹn và **hoàn toàn không làm ảnh hưởng** đến đầu ra mô phỏng của Test Contract:

1. **Nhân vật Mây truyền thống Việt Nam:** Mây đội nón lá tre đan 3D, khăn quàng đỏ bay phất phơ và đèn lồng nhỏ phát sáng ấm.
2. **Hệ thống âm thanh thuật toán Procedural Web Audio:** Tạo âm thanh cho tiếng nhảy, lướt, nhặt bùa gió, cướp đom đóm và chuông tháp đêm 3 hoàn toàn không dùng file ngoài.
3. **Hiệu ứng Bục Nhảy và Bùa Gió:** Đường bay parabol mượt mà khi dẫm bục nhảy, hào quang gió đỏ rực khi kích hoạt Bùa Gió cho phép lướt liên tục.

---

## 5. Cấu trúc Thư mục

```text
├── game.contract.json         # Test Contract v1.1
├── AGENTS.md                  # Harness AI Agent v1.1
├── run_headless.py            # Entry point chạy Headless 60 tick/s
├── run_game.py                # Entry point mở game 3D 3 Đêm
├── requirements.txt           # 0 external packages
├── CREDITS.md                 # Ghi nhận tác quyền
├── src/
│   └── core/
│       └── engine.py          # Lõi mô phỏng toán học tất định 3 Đêm (Contract v1.1)
├── web/
│   ├── index.html             # Game 3D Three.js, HUD 10 ô, 3 Đêm, Pause menu
│   └── js/
│       └── three.min.js       # Thư viện Three.js offline
├── tests/
│   ├── test_headless.py       # Bộ test regression Phase 1 (số liệu chuẩn hóa)
│   └── test_phase2.py         # 8 bộ test chuyên sâu cho tính năng mới Phase 2
└── docs/
    ├── notes/
    │   ├── phase2_spec.md     # Đặc tả nghiệm thu chi tiết Phase 2
    │   ├── assumptions.md     # Giả định thiết kế
    │   ├── token_log.md       # Nhật ký sử dụng AI & theo dõi token
    │   └── retro.md           # Đánh giá & rút kinh nghiệm Phase 2
    └── proof/
        ├── phase-1/           # Bằng chứng Phase 1
        └── phase-2/           # Bằng chứng Phase 2 (Đêm 1, 2, 3, determinism hash)
```
