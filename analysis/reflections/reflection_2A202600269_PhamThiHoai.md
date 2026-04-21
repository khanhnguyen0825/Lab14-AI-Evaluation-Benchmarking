# Reflection Cá Nhân — Lab 14: AI Evaluation Factory

**Họ và tên:** Phạm Thị Hoài  
**Mã sinh viên:** 2A202600269
**Vai trò:** DevOps & Release Gate Engineer
## 1. Engineering Contribution (15đ)
- Tôi chịu trách nhiệm chính cho module kiểm định chất lượng tự động (Regression Gate) và phân tích các chỉ số đánh giá như MRR, Hit Rate, Agreement.
- Tham gia tối ưu pipeline chạy song song bằng cách sử dụng các hàm async để giảm thời gian benchmark.
- Đóng góp commit vào các file: `regression_gate.py`, `runner.py`, chuẩn hóa báo cáo kết quả và logic kiểm định.
- Hỗ trợ nhóm giải thích và xử lý các trường hợp xung đột kết quả giữa các Judge, đảm bảo hệ thống hoạt động ổn định.

## 2. Technical Depth (15đ)
- **MRR (Mean Reciprocal Rank):** Hiểu rõ cách tính và ý nghĩa của MRR trong đánh giá chất lượng truy hồi tài liệu. Đã áp dụng để đo lường vị trí xuất hiện tài liệu đúng đầu tiên.
- **Cohen's Kappa:** Nắm được cách đo độ đồng thuận giữa các Judge, loại trừ yếu tố ngẫu nhiên, giúp đánh giá độ tin cậy của hệ thống Multi-Judge.
- **Position Bias:** Nhận diện và kiểm soát hiện tượng điểm số bị ảnh hưởng bởi vị trí câu trả lời. Đã đề xuất kiểm tra bias khi thay đổi thứ tự đáp án.
- **Trade-off Chi phí vs Chất lượng:** Đánh giá giữa việc dùng model nhỏ để giảm cost/latency và dùng Multi-Judge để tăng chất lượng, từ đó lựa chọn giải pháp cân bằng phù hợp.

## 3. Problem Solving (10đ)
- **Vấn đề 1: Xác định ngưỡng chất lượng phù hợp**
	- Đã thử nghiệm nhiều lần với dữ liệu thực tế, điều chỉnh threshold để hệ thống vừa đảm bảo chất lượng vừa không quá khắt khe.
- **Vấn đề 2: Xử lý lỗi dữ liệu đầu vào**
	- Khi gặp JSON thiếu field hoặc sai kiểu, tôi bổ sung validate schema và fallback giá trị mặc định để pipeline không bị dừng.
- **Vấn đề 3: Tối ưu thời gian chạy benchmark**
	- Chuyển các bước kiểm định sang chạy song song async, giảm đáng kể tổng thời gian chạy mà vẫn giữ chất lượng.

