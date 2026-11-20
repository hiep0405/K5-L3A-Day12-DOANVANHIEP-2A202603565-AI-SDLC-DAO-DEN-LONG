# Đảo Đèn Lồng (Island of Lanterns) — Phát hành v1.0.0

> **Học viên:** Đoàn Văn Hiệp — **MSSV:** 2A202603565 — **Lớp:** K5-L3A  
> **Dự án:** Game 3D Đảo Đèn Lồng qua 4 Phase phát triển bằng quy trình AI SDLC.  
> **Tag nộp:** `phase-4` · **Release:** `v1.0.0` · **Test Contract:** `v1.3`

---

## 1. Giới thiệu Game

**Đảo Đèn Lồng** là một trò chơi 3D mang phong cách cổ tích, ấm áp. Người chơi vào vai **Mây**, người giữ đèn nhỏ tuổi của một hòn đảo lơ lửng giữa biển mây. Trong bóng đêm tĩnh mịch, sương đen và bầy quái vật **Bóng Mực** rình mò nuốt chửng ánh sáng. Nhiệm vụ của Mây là thu thập những đốm sáng đom đóm, thắp lại các ngọn Đèn Lồng Lớn, châm dầu giữ lửa và kiên cường bảo vệ hòn đảo sống sót tới khi bình minh ló rạng.

```text
       ☁️ ☁️ ☁️           🏮 [L1: 100/100]           ☁️ ☁️ ☁️
   ☁️         🏮 [L5: 80/100]        🏮 [L2: 95/100]        ☁️
 ☁️                                                             ☁️
☁️           ✨ (Mote)         🧙 [Mây]          ✨ (Mote)         ☁️
 ☁️                   👾 [Bóng Mực: Drain]                     ☁️
   ☁️         🏮 [L4: 25/100] ⚠️     🏮 [L3: 90/100]        ☁️
       ☁️ ☁️ ☁️      =============================      ☁️ ☁️ ☁️
```

---

## 2. Yêu cầu Hệ thống & Cài đặt Tối đa 3 Lệnh

Game chạy hoàn toàn độc lập, không phụ thuộc thư viện C/GPU ngoài:
- **Hệ điều hành:** Windows 10/11, macOS, hoặc Linux.
- **Python:** Phiên bản 3.8+ (khuyến nghị Python 3.9+).
- **Trình duyệt:** Bất kỳ trình duyệt hiện đại nào hỗ trợ WebGL (Chrome, Edge, Firefox, Safari).

### Cài đặt & Khởi động Nhanh (Tối đa 3 lệnh):
```bash
# Lệnh 1: Cài đặt (Không cần gói ngoài, chỉ dùng Python Standard Library)
python -m pip install -r requirements.txt

# Lệnh 2: Khởi chạy game 3D hoàn chỉnh trên trình duyệt (localhost:8000)
python run_game.py

# Lệnh 3: Chạy toàn bộ 27 bài kiểm thử tự động Test Contract v1.3
python -m unittest discover -s tests -p "test_*.py"
```

---

## 3. Các Công cụ Dòng lệnh Chuẩn (Test Contract v1.3)

### 3.1. Chạy Mô phỏng Tất định (Headless Simulation)
Chạy mô phỏng 60 tick/s không giao diện, xác định 100% bằng seed:
```bash
# Đêm 1 (Đảo Bến - 240s)
python run_headless.py --seed 42 --night 1 --ticks 1200 --out output_night1.jsonl --snapshot-every 10

# Đêm 2 (Đảo Cau - 270s)
python run_headless.py --seed 42 --night 2 --ticks 1200 --out output_night2.jsonl --snapshot-every 10

# Đêm 3 (Đảo Chuông - 300s)
python run_headless.py --seed 42 --night 3 --ticks 1200 --out output_night3.jsonl --snapshot-every 10
```

### 3.2. Đo Hiệu năng Cảnh chuẩn (Benchmark Mode)
Chạy đo đạc cảnh chuẩn (200 Bóng Mực wander, 100 đom đóm, 3 đèn sáng, camera bay vòng tròn 30m):
```bash
python run_bench.py --seed 42 --duration 30 --out bench.json
```
*Kết quả nghiệm thu thực tế:*
- `avg_fps`: **64.2** (ngưỡng đạt $\ge 60$)
- `p1_low_fps`: **57.5** (ngưỡng đạt $\ge 30$)
- `load_ms`: **23.1 ms** (ngưỡng đạt $\le 10000$ ms)
- `peak_mem_mb`: **28 MB** (rất nhẹ và ổn định)

### 3.3. Kiểm thử Ổn định Chạy lâu (Soak Test)
Chạy liên tiếp 10 Đêm liên hoàn trong cùng một tiến trình:
```bash
python run_soak.py --seed 7 --nights 10 --out soak.json
```
*Kết quả nghiệm thu thực tế:*
- `crashes`: **0**
- `mem_start_mb`: **22.0 MB** $\rightarrow$ `mem_end_mb`: **25.5 MB** ($\le 1.2 \times 22.0 = 26.4$ MB, không rò rỉ RAM).
- `duration_s`: **2.9 giây**.

### 3.4. Xuất Bảng Xếp Hạng Cục bộ (Leaderboard Export)
```bash
python run_game.py --export-leaderboard leaderboard_export.json
```

---

## 4. Hướng dẫn Điều khiển & Phím tắt

| Hành động | Phím mặc định | Mô tả |
|---|---|---|
| **Di chuyển** | `W`, `A`, `S`, `D` / `Mũi tên` | Chạy quanh đảo với tốc độ chuẩn $6.0 m/s$ (hoặc $7.2 m/s$ khi có Bùa Gió). |
| **Nhảy** | `Space` | Nhảy với vận tốc $7.0 m/s$, trọng lực $-20 m/s^2$. |
| **Lướt (Dash)** | `Shift` | Lướt tốc độ cao $14 m/s$ trong $0.2s$, hồi chiêu $1.5s$ (không tốn hồi chiêu khi có Bùa Gió). |
| **Thắp đèn / Châm dầu** | `E` | Nạp đom đóm vào đèn gần nhất $\le 2.0m$. Đèn mới: 10 đom, thắp lại: 5 đom, châm dầu: phục hồi 10 fuel/đom. |
| **Tỏa Sáng (Pulse)** | `F` / `Chuột trái` | Tốn 3 đom đóm, hồi chiêu $3.0s$. Choáng Bóng Mực trong $5m$ suốt 120 tick và đẩy lùi $4m$. Thưởng +15 điểm nếu quái đang hút dầu. |
| **Chế độ màu hỗ trợ** | `C` | Bật/tắt nhanh bảng màu tương phản cao hỗ trợ người mù màu. |
| **Tạm dừng** | `P` / `Escape` | Mở menu tạm dừng, bảng xếp hạng và cài đặt. |
| **Xoay Camera** | `Kéo chuột` | Xoay góc nhìn 3D mượt mà tự do 360 độ. |

*Lưu ý:* Mọi phím điều khiển đều có thể đổi tự do trong menu **Cài đặt & Tiếp cận**.

---

## 5. Tính năng Dễ Tiếp Cận (Accessibility)
1. **Đổi phím điều khiển (Key Rebinding):** Tự do gán lại toàn bộ phím điều khiển; hệ thống tự động phát hiện và cảnh báo nếu có phím bị trùng; lưu bền vững trong `localStorage`.
2. **Phụ đề & Chỉ báo hình ảnh:** Cảnh báo nổi bật khi Bóng Mực xuất hiện, Gió Lạc rình mò, 10 giây cuối cùng của đêm và khi đèn lồng sắp cạn dầu ($< 30$ fuel).
3. **Giảm chuyển động (Reduce Motion):** Tùy chọn tắt chớp đỏ màn hình khi bị thương và triệt tiêu rung camera.
4. **Cỡ chữ UI linh hoạt:** Cỡ chữ mặc định $\ge 18$px ở độ phân giải 1280×720, kèm tùy chọn phóng to $\times 1.25$ (22.5px).
5. **Chế độ Mù Màu (Colorblind Mode):** Viền quái chuyển sang màu xanh cyan `#00B3FF`, mắt trắng dạ quang, icon tam giác cảnh báo `⚠` trên đầu đèn yếu.

---

## 6. Sáng tạo của tôi (Creative Additions)
1. **Mô hình Mây mang bản sắc Việt Nam:** Nhân vật Mây đội nón lá tre 3D, khăn quàng đỏ tung bay theo gió và đeo đèn lồng nhỏ phát sáng.
2. **Thanh nhiên liệu 3D Billboard & Hiệu ứng Nhấp nháy 1 Hz:** Thanh dầu 3D tự động xoay hướng theo góc nhìn camera, đổi màu từ xanh sang cam-đỏ khi dầu yếu.
3. **Âm thanh thuật toán Web Audio:** Toàn bộ âm thanh nhảy, lướt, cướp đom đóm, cạn dầu và chuông tháp được tạo hoàn toàn bằng code, 0 tệp âm thanh ngoài.

---

## 7. Cấu trúc Thư mục

```text
├── game.contract.json         # Test Contract v1.3
├── AGENTS.md                  # Harness AI Agent v1.3
├── CHANGELOG.md               # Nhật ký phát hành chi tiết 4 Phase
├── README.md                  # Tài liệu hướng dẫn sử dụng chính
├── LICENSE                    # Giấy phép bản quyền giáo dục
├── CREDITS.md                 # Ghi nhận tác quyền asset, audio & công cụ AI
├── run_game.py                # Server Game 3D & CLI xuất bảng xếp hạng
├── run_headless.py            # Chạy mô phỏng không giao diện 60 tick/s
├── run_bench.py               # Chế độ benchmark đo FPS & tải cảnh chuẩn
├── run_soak.py                # Chế độ soak test kiểm tra rò rỉ RAM 10 đêm
├── bench.json                 # Kết quả đo benchmark nghiệm thu
├── soak.json                  # Kết quả đo soak test nghiệm thu
├── requirements.txt           # 0 external dependencies
├── src/
│   └── core/
│       └── engine.py          # Lõi mô phỏng vật lý & quy tắc game tất định
├── web/
│   ├── index.html             # Bản dựng Web 3D Three.js đầy đủ tính năng
│   └── js/
│       └── three.min.js       # Thư viện Three.js r128 offline
├── data/
│   └── leaderboard.json       # Cơ sở dữ liệu bảng xếp hạng lưu trên đĩa
├── tests/
│   ├── test_headless.py       # Kiểm thử regression Contract v1.3
│   ├── test_phase2.py         # Kiểm thử tính năng 3 Đêm & vật lý
│   ├── test_phase3.py         # Kiểm thử cơ chế Đèn cạn dầu & hút dầu
│   └── test_phase4.py         # Kiểm thử Contract v1.3, Bench, Soak & Leaderboard
└── docs/
    ├── notes/
    │   ├── adr_phase3.md      # Quyết định thiết kế kiến trúc Đèn cạn dầu
    │   ├── token_log.md       # Nhật ký token và chi phí AI qua 4 phase
    │   └── retro.md           # Báo cáo hồi cứu toàn diện 4 phase
    └── proof/                 # Dữ liệu nghiệm thu qua các phase
        ├── phase-1/
        ├── phase-2/
        └── phase-3/
```
