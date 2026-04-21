# Reflection — Pham Thi Hoai

## 1. Tôi đã làm gì trong bài lab này?
- Đọc các file kết quả benchmark trong thư mục `reports/` (summary.json, benchmark_results.json).
- Phân tích các chỉ số đánh giá chất lượng (avg_score, hit_rate, mrr, agreement_rate, cost_usd, delta).
- Thiết kế và hiện thực logic Regression Gate trong file `reports/regression_gate.py` để tự động kiểm tra các tiêu chí chất lượng trước khi release.
- Sinh file kết quả kiểm định tự động `gate_result.json` và quyết định "APPROVE" hoặc "ROLLBACK" release dựa trên các ngưỡng đã đặt ra.

## 2. Kỹ thuật tôi học được
- Cách đọc và phân tích các chỉ số đánh giá hệ thống AI từ file JSON.
- Viết script kiểm định chất lượng tự động bằng Python (Regression Gate).
- Sử dụng các ngưỡng (threshold) để kiểm soát chất lượng release.

## 3. Khó khăn gặp phải và cách giải quyết
- **Khó khăn**: Việc xác định các ngưỡng phù hợp cho từng chỉ số (quality, hit_rate, agreement, cost, delta) để đảm bảo hệ thống vừa đạt chất lượng vừa không quá khắt khe.
- **Giải quyết**: Tham khảo rubric, thử nghiệm nhiều lần với dữ liệu thực tế để điều chỉnh threshold hợp lý.

## 4. Nếu làm lại, tôi sẽ thay đổi gì?
- Có thể bổ sung thêm các cảnh báo chi tiết hơn cho từng chỉ số khi không đạt, giúp nhóm dễ dàng debug và cải thiện hệ thống.
- Tự động gửi thông báo kết quả Regression Gate lên kênh chat nhóm để mọi người nắm được trạng thái release.
