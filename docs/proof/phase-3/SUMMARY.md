# Phase 3 Execution & Test Contract v1.2 Proof Summary

- **Dự án:** Đảo Đèn Lồng (Island of Lanterns)
- **Học viên:** Đoàn Văn Hiệp — MSSV: `2A202603565` — Lớp: `K5-L3A`
- **Phiên bản Contract:** v1.2 (`game.contract.json`)
- **Ticket:** TICKET-03 — CHANGE REQUEST "Đèn cạn dầu"
- **Tag nộp:** `phase-3`

---

## 1. Kết quả Kiểm thử Tự động (Unit & Integration Tests)
Bộ kiểm thử chạy qua `python -m unittest discover -s tests -p "test_*.py"`:

```text
Ran 22 tests in 0.275s

OK
```

### Danh mục các ca kiểm thử chính trong `tests/test_phase3.py`:
1. `test_fuel_decay_and_lantern_out`: Kiểm tra hao hụt nhiên liệu 1.0/giây, sự kiện `lantern_out` khi hết dầu với lý do `"fuel_empty"`, đèn nhớ `ever_lit = True`.
2. `test_refuel_lit_lantern`: Kiểm tra châm dầu đèn đang sáng, sự kiện `refuel` ghi nhận chính xác `motes_used`, `fuel_after`, `player_carried`, điểm số +5/đom đóm.
3. `test_relight_cost_5_and_dynamic_capacity`: Kiểm tra thắp lại đèn đã tắt chỉ tốn 5 đom đóm, thưởng +40 điểm, tăng sức chứa động `new_capacity`.
4. `test_shade_drain_weak_lantern`: Kiểm tra Bóng Mực chuyển sang trạng thái `drain` khi tiếp cận đèn yếu ($< 30$ fuel), phát sự kiện `fuel_drain` gộp.
5. `test_pulse_on_draining_shade_gives_15_score`: Kiểm tra Tỏa Sáng trúng Bóng Mực đang drain thưởng +15 điểm bảo vệ đèn.
6. `test_dawn_insufficient_light_lose`: Kiểm tra thua cuộc khi hết giờ mà không đủ 60% số đèn sáng (`dawn_insufficient_light`).
7. `test_darkness_deadlock_lose`: Kiểm tra thua cuộc tức thì khi rơi vào bế tắc tuyệt đối (`darkness`).
8. `test_dawn_survival_victory`: Kiểm tra chiến thắng khi sống sót tới bình minh với $\ge 60\%$ đèn sáng (`dawn_survived`).

---

## 2. Xác thực Tính Tất định (Determinism Proof)
Chạy hai lần mô phỏng độc lập với `--seed 42 --night 1 --ticks 1200`:
- **Lần chạy 1 (`night1.jsonl`):**
  `SHA256: 8579705E69963FA076302E64123035F5091D494AF242EF6B3D934C4A5CFF323F`
- **Lần chạy 2 (`night1_check.jsonl`):**
  `SHA256: 8579705E69963FA076302E64123035F5091D494AF242EF6B3D934C4A5CFF323F`

$\implies$ **Khớp hoàn toàn 100% từng byte (Zero divergence).**

---

## 3. Các tệp dữ liệu mô phỏng trong Phase 3
- [night1.jsonl](file:///c:/Users/HIEPHIEP/Downloads/day12_vin_ai/K5-L3A-DOANVANHIEP-2A202603565-Day12-AI-SDLC/docs/proof/phase-3/night1.jsonl): 1200 ticks Đêm 1 (Đảo Bến)
- [night2.jsonl](file:///c:/Users/HIEPHIEP/Downloads/day12_vin_ai/K5-L3A-DOANVANHIEP-2A202603565-Day12-AI-SDLC/docs/proof/phase-3/night2.jsonl): 1200 ticks Đêm 2 (Đảo Cau)
- [night3.jsonl](file:///c:/Users/HIEPHIEP/Downloads/day12_vin_ai/K5-L3A-DOANVANHIEP-2A202603565-Day12-AI-SDLC/docs/proof/phase-3/night3.jsonl): 1200 ticks Đêm 3 (Đảo Chuông)
