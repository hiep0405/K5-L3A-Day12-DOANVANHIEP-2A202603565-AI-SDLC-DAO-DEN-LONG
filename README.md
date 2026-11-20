# Đảo Đèn Lồng (Island of Lanterns) — Day 12 AI SDLC

> **Học viên:** Đoàn Văn Hiệp — **MSSV:** 2A202603565 — **Lớp:** K5-L3A  
> **Dự án:** Game 3D Đảo Đèn Lồng qua 4 Phase phát triển bằng quy trình AI SDLC.  
> **Tag:** `phase-1`

---

## 1. Hướng dẫn Cài đặt & Chạy Game (Tối đa 3 lệnh)

Game được thiết kế không phụ thuộc thư viện C/GPU ngoài, chỉ dùng Python Standard Library và Three.js offline:

```bash
# Lệnh 1: Cài đặt (Không cần cài thêm gói ngoài)
python -m pip install -r requirements.txt

# Lệnh 2: Chơi game 3D trực quan trên trình duyệt
python run_game.py

# Lệnh 3: Chạy bộ kiểm thử tự động Test Contract
python -m unittest discover -s tests -p "test_*.py"
```

### Chạy chế độ Headless (Test Contract v1.0)
```bash
python run_headless.py --seed 42 --night 1 --ticks 600 --out output.jsonl --snapshot-every 10
```

---

## 2. Giới thiệu Game & Điều khiển

Bạn vào vai **Mây**, người giữ đèn nhỏ tuổi của Đảo Bến giữa biển mây. Đêm nay sương đen đã nuốt hết ánh sáng. Mây phải gom các đốm sáng (đom đóm) rải rác trên đảo mang về thắp lại **5 Đèn Lồng Lớn** và né tránh **Bóng Mực** trong sương đêm.

* **W, A, S, D / Phím mũi tên:** Di chuyển Mây (hướng di chuyển tương đối theo góc nhìn camera).
* **Space:** Nhảy.
* **E:** Nạp đom đóm vào Đèn Lồng Lớn khi đứng gần (bán kính $\le 2.5m$).
* **F / Chuột trái:** Tỏa Sáng (Pulse) — tốn 1 đom đóm, đẩy lùi và làm choáng Bóng Mực trong $5m$.
* **Kéo chuột:** Xoay tự do góc nhìn camera 3D.

---

## 3. Cách tính điểm (Scoring System)

Điểm số trong game tuân thủ tuyệt đối cấu hình `tuning.score` của Test Contract v1.0:
* **Nhặt 1 đom đóm:** $+10$ điểm.
* **Thắp sáng 1 Đèn Lồng Lớn:** $+100$ điểm.
* **Làm choáng 1 Bóng Mực bằng Tỏa Sáng:** $+20$ điểm.
* **Thưởng khi chiến thắng (thắp đủ 5 đèn):**
  $$\text{Điểm thưởng} = \lfloor \text{Thời gian còn lại (s)} \rfloor \times 1 + \text{Số ngọn lửa (máu) còn lại} \times 50$$

---

## 4. Sáng tạo của tôi (My Creative Additions)

Theo quy định trong mục F của RUBRIC, các yếu tố sáng tạo được tích hợp gọn gàng và **hoàn toàn không làm ảnh hưởng** đến đầu ra mô phỏng của Test Contract:

1. **Nhân vật Mây mang bản sắc văn hóa Việt:** Mây đội nón lá tre đan thủ công 3D (`ConeGeometry`), bên vành nón treo một chiếc đèn lồng hạt tiêu nhỏ xinh đung đưa và phát ánh sáng ấm khi di chuyển.
2. **Hệ thống âm thanh thuật toán tương tác (Procedural Web Audio):** Sử dụng Web Audio API để tổng hợp trực tiếp các tần số âm thanh cổ tích (tiếng đom đóm reo vang, tiếng chuông đồng khi thắp đèn, tiếng nổ tỏa sáng huyền ảo) — không sử dụng bất kỳ file âm thanh ngoài nào, đảm bảo 100% bản quyền và chạy mượt mà.
3. **Hiệu ứng vòng sóng ánh sáng:** Khi kích hoạt Tỏa Sáng (Pulse), một vòng sóng hào quang vàng kim nở rộ từ Mây và lan tỏa quét sạch sương đen xung quanh.

---

## 5. Cấu trúc Thư mục

```text
├── game.contract.json         # Khai báo Test Contract v1.0 và thông số tuning
├── AGENTS.md                  # Quy ước chỉ dẫn cho AI Agent (Harness)
├── run_headless.py            # Entry point chạy Headless 60 tick/s
├── run_game.py                # Entry point mở game 3D trên trình duyệt
├── requirements.txt           # Danh mục thư viện phụ thuộc (0 external package)
├── CREDITS.md                 # Ghi nhận tác quyền và công nghệ sử dụng
├── src/
│   └── core/
│       └── engine.py          # Lõi mô phỏng toán học tất định (Simulation Engine)
├── web/
│   ├── index.html             # Giao diện game 3D Three.js, HUD và Web Audio API
│   └── js/
│       └── three.min.js       # Thư viện Three.js lưu offline cục bộ
├── tests/
│   └── test_headless.py       # Bộ kiểm thử tự động Headless & Scenario
└── docs/
    ├── notes/
    │   ├── assumptions.md     # Giả định thiết kế Phase 1
    │   ├── token_log.md       # Nhật ký sử dụng AI & theo dõi token
    │   └── retro.md           # Đánh giá & rút kinh nghiệm Phase 1
    └── proof/
        └── phase-1/           # Bằng chứng kiểm chứng, log, determinism hash
```

---

## 6. Tài liệu Gốc của Lab

| File | Nội dung |
|---|---|
| [GUIDE.md](GUIDE.md) | Hướng dẫn làm lab: vòng làm việc mỗi phase, harness, kiểm chứng, token |
| [CHECKPOINTS.md](CHECKPOINTS.md) | Các mốc tự kiểm tra từ chuẩn bị đến nộp bài |
| [SUBMISSION.md](SUBMISSION.md) | Đặt tên repo, hạn nộp, tag, Release, video, checklist |
| [RULES.md](RULES.md) | Quy định: AI, trung thực về bằng chứng, bản quyền, bảo mật |
| [RUBRIC.md](RUBRIC.md) | Thang điểm chi tiết |
