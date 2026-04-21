# 📊 Cost Analysis Report

## 1. Chi phí/case

- Tổng chi phí (cost_usd): 0.00768 USD
- Tổng số case: 76
- Chi phí/case: 0.000101 USD

## 2. Chi phí cho 1000 cases

- 0.000101 USD x 1000 = 0.101 USD

## 3. Đề xuất tối ưu chi phí ≥30%

**Cách 1:** Sử dụng model nhỏ hơn (gpt-3.5-turbo hoặc Claude Haiku) cho bước Judge thay vì gpt-4o cho các case dễ, chỉ dùng model mạnh cho case khó/edge-case. Ước tính giảm chi phí Judge ~40%.

**Cách 2:** Áp dụng cache cho các câu hỏi lặp lại hoặc gần giống, tránh gọi LLM nhiều lần cho cùng 1 input. Ước tính giảm chi phí tổng thể ~30%.

**Cách 3:** Tối ưu prompt, rút ngắn context truyền vào model để giảm số token sử dụng mỗi lần gọi.

---

*Báo cáo này dựa trên dữ liệu thật (reports/summary.json). Khi có số liệu mới, cần cập nhật lại các phép tính.*
