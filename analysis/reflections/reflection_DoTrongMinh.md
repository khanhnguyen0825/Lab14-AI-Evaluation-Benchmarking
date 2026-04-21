# Reflection — Đỗ Trọng Minh (AI Judge Engineer)

## 1. Tôi đã làm gì trong bài lab này?
- Chịu trách nhiệm chính xây dựng module `engine/llm_judge.py` đóng vai trò là Giám khảo AI (LLM-as-a-Judge) cho hệ thống Evaluation Factory.
- Triển khai chiến lược chấm điểm đa mô hình (Multi-Judge) bằng cách gọi song song GPT-4o và Claude để đánh giá chéo câu trả lời.
- Xây dựng logic Giải quyết xung đột (Conflict Resolution): Khi 2 model lệch nhau hơn 1 điểm, hệ thống tự động gọi model thứ 3 (`gpt-4o-mini`) làm trọng tài (Tiebreaker) và lấy điểm trung vị.
- Tích hợp và cấu hình hàm `check_position_bias()` để kiểm tra độ thiên vị vị trí của các giám khảo.

## 2. Kỹ thuật tôi học được
- **Xử lý bất đồng bộ (Asynchronous Programming):** Lần đầu ứng dụng thư viện `asyncio` (`asyncio.gather`) để gọi 2 API (OpenAI và Anthropic) cùng lúc, giúp tối ưu và giảm một nửa thời gian chờ so với code tuần tự.
- **Position Bias Mitigation (Khử thiên kiến vị trí):** Hiểu được nguyên lý đổi chỗ (swap) Câu A và Câu B để tránh việc LLM Judge thiên vị luôn chọn câu đầu tiên.

## 3. Khó khăn gặp phải và cách giải quyết
- **Khó khăn về Môi trường và API Key:** Gặp lỗi `ModuleNotFoundError` khi import `anthropic`, sau đó tiếp tục dính lỗi `404 not_found_error` từ phía API của Anthropic (do tài khoản bị giới hạn quyền truy cập vào model cũ `claude-3-haiku-20240307`).
- **Giải quyết:** Tự xử lý lỗi môi trường bằng lệnh `python -m pip install anthropic`. Với lỗi API, mình đã trực tiếp xử lý bằng cách thay thế model sang phiên bản mới được hỗ trợ, đồng thời bọc cấu trúc `try-except` cẩn thận để hệ thống luôn trả về điểm mặc định (fallback = 3) kèm log giải thích chi tiết thay vì bị văng (crash) giữa chừng.

## 4. Nếu làm lại, tôi sẽ thay đổi gì?
- Thay vì chỉ bắt LLM trả về 1 điểm số tổng hợp (`score`) cho câu trả lời, mình sẽ chia nhỏ prompt yêu cầu model trả về điểm cho từng tiêu chí riêng biệt (Accuracy: 5, Tone: 4, Completeness: 3,...) để file báo cáo cuối cùng chi tiết hơn.
- Cải thiện thêm logic xử lý rate limit (Timeout/Retry) bằng thư viện như `tenacity` để đảm bảo hệ thống vững vàng hơn khi phải chạy mẻ lớn (batch size) trên 500 hoặc 1000 test cases.
