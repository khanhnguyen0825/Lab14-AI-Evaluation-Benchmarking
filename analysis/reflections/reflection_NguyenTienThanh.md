# Reflection — Nguyễn Tiến Thành (Project Leader & Analyst)

## 1. Engineering Contribution (Đóng góp kỹ thuật)
Trong bài lab này, tôi đảm nhiệm vai trò **Project Leader** và **Lead Analyst**. Các đóng góp cụ thể của tôi bao gồm:
- **Thiết kế Data Contract**: Xây dựng cấu trúc JSON Schema thống nhất ngay từ đầu để đảm bảo 5 thành viên có thể phát triển module độc lập (Decoupling) và ráp nối không lỗi.
- **Phát triển logic Release Gate**: Phối hợp cùng nhóm DevOps thiết kế hệ thống kiểm soát chất lượng tự động (`regression_gate.py`), sử dụng các ngưỡng (Thresholds) về Accuracy, Hit Rate và Cost để ra quyết định Deploy.
- **Phân tích Failure Clustering**: Trực tiếp phân loại 76 test cases thành các nhóm lỗi kỹ thuật (Hallucination, Retrieval Error, Prompt Leakage) để xác định điểm yếu của hệ thống.

## 2. Technical Depth (Chiều sâu kỹ thuật)
Tôi đã nghiên cứu và áp dụng các khái niệm đo lường chuyên sâu:
- **MRR (Mean Reciprocal Rank)**: Thay vì chỉ dùng Hit Rate, tôi áp dụng MRR để đánh giá vị trí của tài liệu đúng trong kết quả trả về. Nếu tài liệu đúng nằm ở top-1, hệ thống đạt điểm tối đa, giúp phản ánh chính xác hiệu quả của bộ Retriever.
- **Hệ số đồng thuận (Agreement Rate/Cohen's Kappa)**: Tôi giám sát việc triển khai Multi-Judge Consensus. Chúng tôi đo lường mức độ đồng thuận giữa GPT-4o và Claude để đảm bảo tính khách quan (Eliminating Single-Model Bias).
- **Position Bias**: Nhận thức được xu hướng LLM ưu tiên các thông tin xuất hiện ở đầu hoặc cuối context (Lost in the Middle), tôi đã chỉ đạo nhóm Judge thực hiện `check_position_bias` bằng cách đảo thứ tự context để kiểm chứng độ chính xác.
- **Trade-off Chi phí & Chất lượng**: Tôi đã tối ưu hóa chi phí bằng cách sử dụng `gpt-4o-mini` cho các tác vụ phân loại cơ bản và chỉ dùng `gpt-4o` cho bước trọng tài (Tiebreaker), giúp giảm 70% chi phí mà vẫn giữ được độ tin cậy.

## 3. Problem Solving (Giải quyết vấn đề)
Vấn đề lớn nhất nhóm gặp phải là **Xung đột Interface** khi tích hợp 5 module Async khác nhau:
- **Giải pháp**: Tôi đã áp dụng mô hình **Integration Sprint** ở giờ thứ 2, yêu cầu các thành viên cung cấp Mock Data dựa trên Data Contract đã ký. Điều này giúp phát hiện sớm các lỗi bất đồng bộ (Race conditions) và lỗi parse JSON trước khi chạy benchmark thật.
- **Kết quả**: Toàn bộ hệ thống pipeline đã chạy thành công 76 cases trong chưa đầy 2 phút, đạt chuẩn Performance yêu cầu.

## 4. Bài học kinh nghiệm
Nếu có thêm thời gian, tôi sẽ triển khai thêm bước **Semantic Chunking** để giải quyết triệt để lỗi "Context Noise" mà tôi đã phát hiện trong phần Phân tích 5 Whys, từ đó nâng điểm Faithfulness của hệ thống lên trên 0.95.
