# Reflection (Person 2)
# Ha Hung Phuoc - 2A202600367

## 1. Tôi đã làm gì trong bài lab này?
- **Xây dựng hệ thống Multi-Judge Evaluation** trong `engine/llm_judge.py` sử dụng 2 model: GPT-4o-mini (đánh giá nhanh) và Claude Haiku (xác thực lại). Cơ chế này giúp giảm tỷ lệ sai lệch cá nhân của từng model.
- **Implement Conflict Resolution Logic**: Khi hai Judge có điểm lệch nhau > 1.0, hệ thống tự động gọi model thứ 3 (Tiebreaker) để đạt consensus. Nếu tiebreaker không có hoặc cũng khác, chọn điểm trung bình.
- **Phát triển module `check_position_bias`** để kiểm tra xem Judge có bị ảnh hưởng bởi vị trí (early/late) của đáp án hay không.
- **Error Handling & Fallback Mechanism**: Xây dựng cơ chế fallback khi API gặp lỗi (ví dụ: Claude timeout, OpenAI rate limit) để đảm bảo benchmark không bị gián đoạn.

## 2. Kỹ thuật tôi học được
- **Multi-model Evaluation Framework**: Cách thiết kế kiến trúc để kết hợp nhiều LLM khác nhau, không chỉ đơn thuần gọi tuần tự mà phải tối ưu latency với `asyncio.gather()`.
- **Async Concurrency Patterns**: Gọi GPT-4o-mini + Claude Haiku đồng thời, tập hợp kết quả bằng `asyncio.gather()` để giảm thời gian chờ từ O(n) xuống O(1) (nếu đủ compute resources).
- **API Error Handling & Resilience**: Xử lý các tình huống API thất bại (timeout, rate limiting, invalid response) mà không làm crash toàn bộ pipeline.
- **JSON Schema Validation**: Sử dụng Pydantic models để validate response từ các model, giúp detect malformed JSON sớm.
- **Scoring Consensus Algorithms**: Thiết kế logic để hòa giải khi có conflict giữa 2 scores, quan trọng trong multi-judge scenarios.

## 3. Khó khăn gặp phải và cách giải quyết
- **Khó khăn 1 - Inconsistent API Responses**: Các model trả về format JSON khác nhau (Claude quên trả về score field, GPT-4o trả về string thay vì int), gây lỗi khi parsing.
  - **Giải quyết**: Thêm validation layer bằng Pydantic model với type hints rõ ràng, sử dụng `.parse_obj()` để auto-cast, và thêm detailed error messages.
  
- **Khó khăn 2 - Low Agreement Rate (19.1%)**: Sau khi chạy full benchmark 76 cases, agreement_rate chỉ 19.1% (Claude trả về score 3 cho tất cả cases do API error).
  - **Giải quyết**: Debug bằng cách in reasoning string từ cả 2 judges, phát hiện Claude bị error "Error calling Anthropic API". Xác minh lại Claude API key, thấy rằng errors chỉ là do connection issue tạm thời. Sau khi refresh key, agreement rate tăng lên 77.63%.
  
- **Khó khăn 3 - Latency Budget**: Chạy 2 judges cho 76 cases có thể vượt quá 2 phút budget nếu gọi sequential.
  - **Giải quyết**: Sử dụng `asyncio.gather()` để gọi đồng thời, kết hợp với batch processing (batch_size=10) để tối ưu throughput mà không vượt rate limit.

- **Khó khăn 4 - Conflict Resolution Edge Cases**: Khi 2 judges hoàn toàn không đồng ý (VD: score 5 vs 2), cần quyết định việc fallback như thế nào.
  - **Giải quyết**: Implement tiebreaker logic: nếu |score_a - score_b| > 1.0, gọi model thứ 3; nếu không, chọn trung bình. Thêm logging để track bao nhiêu cases cần tiebreaker.

## 4. Nếu làm lại, tôi sẽ thay đổi gì?
- **Sử dụng structured outputs (JSON mode) từ đầu**: Thay vì dựa vào model tự trả về JSON, sử dụng OpenAI's `json_schema` parameter hoặc Claude's `raw_response` mode để đảm bảo format luôn nhất quán.
- **Thêm mais detailed rubrics**: Thay vì chỉ cho điểm 1-5 tổng quát, chia thành các tiêu chí: (1) Tính chính xác, (2) Tính đầy đủ, (3) Tính liên quan, (4) Tính rõ ràng. Mỗi tiêu chí 1-5 điểm, sau đó trung bình.
- **Implement timeout mechanism**: Thêm timeout cho từng API call (VD: 10 giây) để tránh hanging khi model slow.
- **Better logging & monitoring**: Log toàn bộ request/response (không chỉ summary) vào file để dễ debug issues như Claude API errors.
- **Diversify judge models**: Thay vì chỉ dùng GPT-4o + Claude, thêm LLaMA hoặc Gemini để có broader perspective, nhất là với Vietnamese content.
- **A/B test different conflict resolution strategies**: Implement multiple strategies (average, weighted, voting, max-disagreement-rejection) và compare metrics để chọn optimal approach.
