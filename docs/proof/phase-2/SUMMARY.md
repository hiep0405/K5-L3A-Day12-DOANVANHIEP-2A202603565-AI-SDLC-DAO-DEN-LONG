# Bằng chứng kiểm chứng Phase 2 (Verification Proofs — Ticket-02)

Dự án: **Đảo Đèn Lồng** — Phase 2
Sinh viên: **Đoàn Văn Hiệp** — MSSV: **2A202603565**

## Bảng đối chiếu Yêu cầu và Bằng chứng (Traceability Matrix)

| STT | Yêu cầu kiểm chứng | Cách thức kiểm chứng | File bằng chứng | Kết quả |
|---|---|---|---|---|
| 1 | Test Contract v1.1 với snapshot mở rộng | Chạy `run_headless.py` với Đêm 1, 2, 3 | `docs/proof/phase-2/night2_run.jsonl` | **ĐẠT** (Đủ mảng motes, drifters, charms, wind) |
| 2 | Tính tất định Đêm 2 (Determinism) | Chạy 2 lần riêng biệt seed 42 so sánh mã SHA-256 | `docs/proof/phase-2/determinism_check.txt` | **ĐẠT** (`Match: True`, trùng khớp 100%) |
| 3 | Cơ chế Lướt (Dash 14 m/s) | Test scenario kích hoạt Dash | `tests/test_phase2.py::test_dash_mechanic` | **ĐẠT** (Tốc độ 14 m/s, giữ độ cao trên không) |
| 4 | Bùa Gió (Wind Charm) | Test nhặt bùa C1, tăng tốc 7.2 m/s, bỏ hồi chiêu Dash | `tests/test_phase2.py::test_wind_charm_pickup_and_speedup` | **ĐẠT** (Phát event `charm_picked`, 600 ticks) |
| 5 | Gió Lạc (Drifters cướp & rơi đom đóm) | Test Gió Lạc cướp khi carried $\ge 5$, Tỏa Sáng làm rơi đồ | `tests/test_phase2.py::test_drifter_steal_and_pulse_drop` | **ĐẠT** (Phát event `drifter_steal`, `drifter_drop`) |
| 6 | Bục Nhảy (Jump Pads) | Test Mây dẫm bục phóng sang đảo đối diện | `tests/test_phase2.py::test_jump_pad_launch` | **ĐẠT** (Vận tốc Y 14 m/s, ngang 24 m/s chuẩn xác) |
| 7 | Rơi khỏi đảo (Y < -10) | Test kiểm tra rơi đảo trừ máu, mất đom đóm, hồi sinh sau 60 tick | `tests/test_phase2.py::test_falling_off_island_penalty` | **ĐẠT** (Phát event `player_hit` với `lost: True`) |
| 8 | Cơ chế Tạm dừng (Pause) | Test input pause, sim_tick đứng yên | `tests/test_phase2.py::test_pause_mechanism` | **ĐẠT** (Snapshot ghi `state: "paused"`) |
| 9 | Đêm 3 Đảo Chuông & Gió mạnh | Test load map 3 tầng, tháp chuông, 7 đèn, chu kỳ gió | `tests/test_phase2.py::test_night3_map_and_wind` | **ĐẠT** (Map 7 đèn, 2 bùa gió C1/C2) |
| 10 | Hiệu năng mô phỏng Headless | Benchmark chạy 6000 tick dưới 5 giây | `tests/test_phase2.py::test_full_night_performance` | **ĐẠT** (21.600 tick xong trong < 1.0 giây, chỉ tiêu $\le 30$s) |
| 11 | Hồi quy Phase 1 (Regression) | Chạy toàn bộ test của Phase 1 với số liệu chuẩn | `tests/test_headless.py` | **ĐẠT** (Tất cả test Phase 1 đều pass) |
