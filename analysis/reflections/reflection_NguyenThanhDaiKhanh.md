# Reflection — Người 1 (Data & Retrieval Engineer)

## 1. Tôi đã làm gì trong bài lab này?
Trong dự án này, tôi chịu trách nhiệm xây dựng nền tảng dữ liệu cho toàn bộ hệ thống Evaluation Factory. Cụ thể:
- **Thiết kế Pipeline SDG (Synthetic Data Generation):** Tôi đã xây dựng script `data/synthetic_gen.py` để tự động hóa việc đọc tài liệu gốc từ folder `data/docs/`, thực hiện chia nhỏ văn bản (Chunking) với kỹ thuật chồng lấp (Overlap) để giữ ngữ cảnh.
- **Xây dựng Golden Dataset:** Tạo ra bộ 76 test cases chất lượng cao, bao gồm cả các trường hợp khó (Red Teaming) như Prompt Injection và Out-of-Scope để thử thách Agent.
- **Phát triển module Retrieval Evaluation:** Implement logic tính toán Hit Rate và MRR (Mean Reciprocal Rank) trong `engine/retrieval_eval.py` để đo lường độ chính xác của bộ lọc tài liệu.
- **Đồng bộ hóa dữ liệu nhóm:** Tạo ra `chunk_map.json` để chia sẻ tài nguyên cho Người 3 triển khai Agent, đảm bảo tính thống nhất về ID tài liệu trong toàn bộ hệ thống.

## 2. Kỹ thuật tôi học được
- **Recursive Character Chunking:** Hiểu sâu về cách chia nhỏ văn bản mà không làm mất ý nghĩa giữa các đoạn, giúp tăng Hit Rate của hệ thống RAG.
- **Xử lý lỗi hệ thống trên Windows:** Kinh nghiệm thực tế trong việc cấu hình `sys.stdout` để xử lý triệt để lỗi `UnicodeEncodeError` khi làm việc với tiếng Việt trên Terminal của Windows.
- **Red Teaming cho AI:** Cách tư duy như một "hacker" để tạo ra những câu hỏi đánh lừa AI, từ đó đánh giá sự an toàn và tin cậy của Agent.

## 3. Khó khăn gặp phải và cách giải quyết
- **Khó khăn:** Ban đầu, khi làm việc trên môi trường Windows, toàn bộ script bị crash khi in kết quả tiếng Việt ra màn hình.
- **Giải quyết:** Tôi đã nghiên cứu và áp dụng kỹ thuật `reconfigure(encoding="utf-8")` cho stdout và dùng `json.dumps(ensure_ascii=False)` để đảm bảo dữ liệu hiển thị chính xác mà không làm gián đoạn pipeline.
- **Khó khăn:** Việc đồng bộ ID tài liệu cho các thành viên khác dẫn đến Hit Rate bị thấp (chỉ ~19.1%) ở máy của đồng đội.
- **Giải quyết:** Tôi đã chuẩn hóa file `chunk_map.json` và hướng dẫn nhóm cách sử dụng chung một file `golden_set.jsonl` duy nhất để đảm bảo kết quả Benchmark nhất quán giữa mọi máy tính.

## 4. Nếu làm lại, tôi sẽ thay đổi gì?
- **Sử dụng Semantic Chunking:** Nếu có thời gian, tôi sẽ áp dụng chunking dựa trên ngữ nghĩa (dùng Embedding) thay vì chỉ dùng độ dài ký tự để các đoạn văn bản tách bạch hơn theo chủ đề.
- **Hybrid Search:** Tôi muốn kết hợp tìm kiếm từ khóa truyền thống với tìm kiếm vector (Vector Search) để tối ưu hóa khả năng truy xuất thông tin cho Agent.
