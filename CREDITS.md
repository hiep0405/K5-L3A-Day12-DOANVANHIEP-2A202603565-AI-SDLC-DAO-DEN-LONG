# Ghi nhận Tác quyền & Nguồn lực (CREDITS)

Dự án: **Đảo Đèn Lồng (Island of Lanterns)** — Phát hành v1.0.0 (Day 12 AI SDLC)
Tác giả / Lập trình viên: **Đoàn Văn Hiệp** — MSSV: **2A202603565** — Lớp: **K5-L3A**

---

## 1. Thành phần Đồ họa & Mô hình 3D (Visual Assets)
- Nhân vật Mây (nón lá, áo dài mộc, khăn quàng đỏ, lồng đèn mini), các Đèn Lồng Lớn, Đom Đóm, Bóng Mực, Gió Lạc và địa hình 3 hòn đảo được dựng hoàn toàn bằng mã nguồn procedural mesh nguyên bản với Three.js r128 (không sử dụng mô hình 3D ngoài tải từ internet).
- Bảng màu chuẩn hoá: vàng cam ấm (#F2C14E, #FFB347), tím bóng đêm (#7A3CFF), xanh biển đêm (#0E1430, #1B2350), đỏ khăn quàng (#C8102E).

---

## 2. Hệ thống Âm thanh Thuật toán (Procedural Audio)
- Toàn bộ âm thanh trong game (nhảy, lướt, nhặt đom đóm, nạp đèn, đèn sáng, tỏa sáng, bị tấn công, rơi đài, bục nhảy, cướp đom đóm và đèn cạn dầu) được tổng hợp trực tiếp bằng Web Audio API với bộ dao động OscillatorNode & GainNode, không sử dụng bất kỳ tệp âm thanh bên ngoài nào (.mp3, .wav).

---

## 3. Thư viện & Công cụ (Libraries & Frameworks)
- **Three.js r128:** Thư viện đồ hoạ 3D WebGL (bản phân phối tĩnh cục bộ tại `web/js/three.min.js`, có thể chơi hoàn toàn offline).
- **Python 3 Standard Library:** Toàn bộ công cụ mô phỏng (`src/core/engine.py`), headless (`run_headless.py`), benchmark (`run_bench.py`), soak test (`run_soak.py`), web server & bảng xếp hạng (`run_game.py`) chạy hoàn toàn trên thư viện tiêu chuẩn của Python, 0 dependency ngoài.

---

## 4. Công cụ AI Hỗ trợ Phát triển (AI Development Tools)
- **Google Antigravity AI Agent & DeepMind Models:** Hỗ trợ phân tích PRD, chuyển đổi yêu cầu thành Test Contract, sinh kịch bản kiểm thử, kiểm thử hồi quy và tối ưu hoá mã nguồn.
- Toàn bộ quy trình tuân thủ quy chuẩn Software Development Lifecycle tích hợp AI (AI SDLC) với nhật ký token minh bạch tại `docs/notes/token_log.md` và báo cáo hồi cứu tại `docs/notes/retro.md`.
