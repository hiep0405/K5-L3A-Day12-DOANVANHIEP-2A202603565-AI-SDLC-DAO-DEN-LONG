# Bằng chứng kiểm chứng Phase 1 (Verification Proofs)

Dự án: **Đảo Đèn Lồng** — Phase 1
Sinh viên: **Đoàn Văn Hiệp** — MSSV: **2A202603565**

## Bảng đối chiếu Yêu cầu và Bằng chứng (Traceability Matrix)

| STT | Yêu cầu kiểm chứng | Cách thức kiểm chứng | File bằng chứng | Kết quả |
|---|---|---|---|---|
| 1 | Chế độ Headless 60 tick/s theo Test Contract v1.0 | Chạy `run_headless.py` với seed 42, 300 ticks | `docs/proof/phase-1/run_default.jsonl` | **ĐẠT** (JSONL chuẩn: snapshot, event, end) |
| 2 | Tính tất định (Deterministic Simulation) | Chạy 2 lần cùng seed 42 và so sánh SHA-256 Hash | `docs/proof/phase-1/determinism_check.txt` | **ĐẠT** (`Match: True`, cùng mã Hash) |
| 3 | Thu gom đom đóm (Mote pickup) | Test đơn vị kịch bản nhặt đom đóm trong bán kính 1.5m | `tests/test_headless.py` | **ĐẠT** (Phát event `mote_picked`, carried tăng) |
| 4 | Nạp đom đóm và Thắp Đèn Lớn (Deposit & Lit) | Test đơn vị kịch bản nạp đủ 5 đom đóm vào đèn L1 | `tests/test_headless.py` | **ĐẠT** (Phát event `deposit`, `lantern_lit`) |
| 5 | Tỏa sáng làm choáng Bóng Mực (Pulse Stun) | Test đơn vị kích hoạt Pulse, đẩy lùi 2m và stun 3s | `tests/test_headless.py` | **ĐẠT** (Phát event `pulse`, list `stunned_ids`) |
| 6 | Bóng Mực tấn công, mất máu, rơi đom đóm | Test va chạm với Bóng Mực khi hết máu | `tests/test_headless.py` | **ĐẠT** (Phát event `player_hit`, rơi 50%, `game_over`) |
| 7 | Thắng game khi thắp đủ 5 đèn | Test kịch bản cả 5 đèn đều sáng | `tests/test_headless.py` | **ĐẠT** (`state: "won"`, `reason: "all_lit"`) |
| 8 | Xử lý lỗi Input / Scenario (Exit code 2) | Chạy headless với file scenario không tồn tại | `tests/test_headless.py` | **ĐẠT** (Mã thoát đúng 2, in stderr) |
| 9 | Game 3D trực quan có giao diện | Chạy `python run_game.py`, chơi trên trình duyệt | `web/index.html` | **ĐẠT** (Three.js 3D mượt mà, có nón lá, âm thanh, HUD) |
