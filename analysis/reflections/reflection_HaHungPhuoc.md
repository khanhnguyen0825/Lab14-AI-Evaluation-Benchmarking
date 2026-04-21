# Reflection (Person 2)
# Ha Hung Phuoc - 2A202600367

## 1. Engineering Contribution (15đ)
- Tôi chịu trách nhiệm chính cho module [engine/llm_judge.py](engine/llm_judge.py), bao gồm thiết kế cơ chế Multi-Judge để chấm điểm bằng 2 model độc lập.
- Tôi implement Conflict Resolution: khi chênh lệch điểm giữa hai judge lớn hơn ngưỡng, hệ thống gọi tiebreaker để tránh kết luận thiếu ổn định.
- Tôi phát triển và tích hợp kiểm tra Position Bias để đánh giá mức độ công bằng khi thay đổi thứ tự đáp án.
- Tôi tối ưu luồng async bằng `asyncio.gather()` để giảm thời gian chờ API và giữ benchmark chạy ổn định trên tập 76 cases.
- Đóng góp được thể hiện qua các commit cập nhật logic đánh giá, xử lý lỗi API, và chuẩn hóa output JSON trong các file judge/eval liên quan.

## 2. Technical Depth (15đ)
- **MRR (Mean Reciprocal Rank)**: đo chất lượng retrieval qua vị trí tài liệu đúng đầu tiên. Tài liệu đúng xuất hiện càng sớm thì điểm càng cao.
- **Cohen's Kappa**: đo mức đồng thuận giữa các judge sau khi loại trừ phần đồng thuận ngẫu nhiên, phù hợp để đánh giá độ tin cậy của Multi-Judge.
- **Position Bias**: hiện tượng điểm số thay đổi do vị trí câu trả lời (đầu/cuối) thay vì chất lượng thực. Tôi dùng module kiểm tra bias để phát hiện và giảm rủi ro này.
- **Trade-off Chi phí vs Chất lượng**:
  - Dùng model nhẹ hơn giúp giảm cost và latency nhưng có thể giảm độ ổn định của đánh giá.
  - Dùng Multi-Judge + tiebreaker tăng chất lượng và độ tin cậy, nhưng tốn thêm token và thời gian.
  - Giải pháp tôi chọn là chỉ gọi tiebreaker khi cần (disagreement cao) để cân bằng hiệu năng và chi phí.

## 3. Problem Solving (10đ)
- **Vấn đề 1: API trả dữ liệu không đồng nhất**
  - Triệu chứng: JSON thiếu field hoặc sai kiểu dữ liệu, gây lỗi parse.
  - Cách xử lý: thêm lớp validate schema, ép kiểu an toàn, và fallback giá trị mặc định để pipeline không dừng.
- **Vấn đề 2: Agreement rate thấp bất thường**
  - Triệu chứng: chênh lệch điểm lớn trên nhiều case do một judge gặp lỗi kết nối/API.
  - Cách xử lý: bổ sung logging reasoning/response theo từng judge, khoanh vùng nguyên nhân, sau đó điều chỉnh cấu hình và cơ chế fallback.
- **Vấn đề 3: Nguy cơ vượt thời gian benchmark**
  - Triệu chứng: chạy tuần tự 2 judge làm tăng latency toàn hệ thống.
  - Cách xử lý: chuyển sang gọi song song async theo batch, giảm đáng kể tổng thời gian chạy mà vẫn giữ chất lượng.

## 4. Tự đánh giá và hướng cải thiện
- Tôi hoàn thành đúng phần việc kỹ thuật cốt lõi của Person 2: thiết kế judge pipeline, xử lý conflict, và kiểm soát bias.
- Nếu làm lại, tôi sẽ bổ sung thêm rubric chi tiết theo từng tiêu chí con (độ chính xác, độ đầy đủ, tính liên quan, tính rõ ràng) để tăng tính giải thích của điểm số.
