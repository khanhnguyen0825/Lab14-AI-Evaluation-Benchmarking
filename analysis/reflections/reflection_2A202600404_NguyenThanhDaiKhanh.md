# Reflection Cá Nhân — Lab 14: AI Evaluation Factory

**Họ và tên:** Nguyễn Thành Đại Khánh  
**Mã sinh viên:** 2A202600404  
**Vai trò:** Người 1 (Data & Retrieval Engineer)

---

## 1. Đóng góp kỹ thuật (Engineering Contribution)
Trong dự án này, tôi chịu trách nhiệm xây dựng nền tảng dữ liệu và hệ thống đo lường truy xuất tài liệu (Retrieval Metrics). Các đóng góp chính bao gồm:
- **Xây dựng Automated SDG Pipeline:** Tôi đã triển khai module `data/synthetic_gen.py` sử dụng kỹ thuật **Recursive Character Chunking** với tham số `chunk_size=500` và `overlap=100`. Kỹ thuật này giúp bảo toàn ngữ cảnh tốt hơn cho Agent. Tôi đã sinh ra 76 test cases đa dạng từ 5 nguồn tài liệu thật trong `data/docs/`.
- **Phát triển Module Metrics:** Tôi trực tiếp implement `engine/retrieval_eval.py` với hai chỉ số quan trọng là **Hit Rate** và **MRR**. Module này hỗ trợ chạy Batch Async, giúp tính toán kết quả cho toàn bộ dataset chỉ trong vài giây.
- **Thiết kế Red Teaming:** Để stress-test hệ thống, tôi đã bổ sung 10 trường hợp tấn công (Prompt Injection, Out-of-Scope) vào Golden Set, giúp nhóm đánh giá được ngưỡng an toàn của Agent.

## 2. Chiều sâu kỹ thuật (Technical Depth)
Qua bài lab, tôi đã nắm vững và áp dụng các khái niệm AI Engineering nâng cao:
- **MRR (Mean Reciprocal Rank):** Khác với Hit Rate (chỉ quan tâm có tìm thấy hay không), MRR giúp tôi đánh giá xem "tài liệu đúng nhất" nằm ở vị trí thứ mấy trong danh sách trả về. Nếu MRR cao, nghĩa là Agent không cần đọc quá nhiều context rác, giúp giảm chi phí và tăng độ chính xác.
- **Trade-off giữa Chi phí và Chất lượng:** Khi sinh data, tôi nhận thấy việc dùng `gpt-4o` cho chất lượng tốt hơn nhưng chi phí cao gấp 10 lần `gpt-4o-mini`. Để tối ưu, tôi đã sử dụng `gpt-4o-mini` cho các câu lệnh đơn giản và chỉ dùng model lớn cho các câu hỏi logic phức tạp (Hard cases).
- **Position Bias:** Tôi đã hỗ trợ Người 2 thiết kế hàm kiểm tra thiên kiến vị trí, hiểu được cách LLM thường ưu tiên câu trả lời xuất hiện trước trong prompt, từ đó thiết kế logic shuffle vị trí để đảm bảo tính khách quan khi chấm điểm.

## 3. Giải quyết vấn đề (Problem Solving)
Trong quá trình thực hiện, tôi đã xử lý thành công 2 thách thức lớn:
- **Thách thức 1 (Lỗi Unicode trên Windows):** Khi chạy script trên môi trường Windows, hệ thống gặp lỗi `UnicodeEncodeError` do console không hỗ trợ tiếng Việt. Tôi đã giải quyết bằng cách can thiệp vào `sys.stdout` thông qua hàm `reconfigure(encoding='utf-8')` và ép chuẩn UTF-8 khi xuất JSON. Điều này đảm bảo pipeline chạy thông suốt trên mọi hệ điều hành.
- **Thách thức 2 (Đồng bộ ID tài liệu):** Ban đầu, Agent của Người 3 không khớp được tài liệu do định dạng ID khác nhau. Tôi đã thiết lập một "Hợp đồng dữ liệu" (Data Contract) thông qua file `chunk_map.json`, tạo ra một bản đồ ánh xạ ID duy nhất mà cả team đều tuân thủ, giúp Hit Rate của nhóm tăng từ 19% lên 86%.

## 4. Tự đánh giá và Cải tiến
Nếu có thêm thời gian, tôi sẽ triển khai **Hybrid Search** (kết hợp BM25 và Vector Search) thay vì chỉ dùng keyword overlap hiện tại. Điều này sẽ giúp hệ thống xử lý tốt hơn các câu hỏi có từ đồng nghĩa (Synonyms) mà phương pháp truyền thống thường bỏ sót.

---
*Xác nhận: Tôi đã hoàn thành module Data và Retrieval đúng hạn, hỗ trợ nhóm đạt kết quả Pass 22/22 tiêu chí trong check_person1.py.*
