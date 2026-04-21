# 📋 PHÂN CHIA CÔNG VIỆC NHÓM — Lab 14: AI Evaluation Factory

> **Dành cho:** Toàn bộ thành viên nhóm + AI Agent hỗ trợ coding  
> **Mục tiêu:** Hoàn thiện toàn bộ hệ thống Evaluation Factory để đạt điểm tối đa  
> **Thời gian:** 4 giờ làm việc

---

## 🗺️ Tổng quan kiến trúc hệ thống & Luồng dữ liệu

```
[Người 1] data/synthetic_gen.py
        ↓ sinh ra
data/golden_set.jsonl  ── (INPUT cho toàn bộ hệ thống)
        ↓
[Người 2] engine/llm_judge.py  +  [Người 3] engine/runner.py
        ↓ cả hai kết hợp lại trong
[Người 3] main.py  ── gọi agent/main_agent.py + engine/retrieval_eval.py
        ↓ sinh ra
reports/summary.json + reports/benchmark_results.json
        ↓
[Người 4] Đọc reports/ → Viết logic Regression Gate
[Người 5] Đọc reports/ → Viết analysis/failure_analysis.md
```

> **Nguyên tắc làm việc:**  
> Tất cả code song song ngay từ đầu bằng **Mock Data**.  
> Giai đoạn cuối (sau 1.5 giờ) mới ráp nối (Integration).  
> Mỗi người tự `git commit` code của mình lên **branch riêng** theo tên: `feature/person-X`.

---

## 📌 Hợp đồng Dữ liệu (Data Contract) — Đọc trước khi code

> **Tất cả 5 người phải đồng thuận với format này trước khi tản ra làm việc độc lập.**

### Format 1 item trong `data/golden_set.jsonl`
```json
{
  "id": "case_001",
  "question": "Làm thế nào để đổi mật khẩu tài khoản?",
  "expected_answer": "Vào mục Cài đặt → Bảo mật → Đổi mật khẩu.",
  "context": "Đoạn văn bản từ tài liệu gốc...",
  "expected_retrieval_ids": ["doc_policy_v2", "doc_faq_section3"],
  "metadata": {
    "difficulty": "easy",
    "type": "fact-check",
    "category": "security"
  }
}
```

### Format `reports/summary.json` (bắt buộc để `check_lab.py` pass)
```json
{
  "metadata": {
    "version": "Agent_V2_Optimized",
    "total": 50,
    "timestamp": "2026-04-21 10:00:00"
  },
  "metrics": {
    "avg_score": 4.2,
    "hit_rate": 0.86,
    "mrr": 0.73,
    "agreement_rate": 0.81,
    "cost_usd": 0.45,
    "total_tokens": 38000
  },
  "regression": {
    "v1_avg_score": 3.8,
    "v2_avg_score": 4.2,
    "delta": 0.4,
    "decision": "APPROVE"
  }
}
```

---

---

# 👤 NGƯỜI 1 — Data & Retrieval Engineer

## 📁 File phụ trách
| File | Trạng thái ban đầu | Nhiệm vụ |
|---|---|---|
| `data/synthetic_gen.py` | Có skeleton (TODO) | **Implement hoàn toàn** |
| `engine/retrieval_eval.py` | Có skeleton (TODO) | **Implement hoàn toàn** |
| `data/golden_set.jsonl` | Chưa có | **Tạo ra bằng cách chạy script** |

## 🎯 Mục tiêu cụ thể
- [ ] Tạo ra file `data/golden_set.jsonl` với **đúng 50+ test cases** đúng format Data Contract ở trên.
- [ ] Implement hàm `calculate_hit_rate()` và `calculate_mrr()` trong `engine/retrieval_eval.py`.
- [ ] Implement hàm `evaluate_batch()` để chạy được eval cho toàn bộ dataset.
- [ ] Viết thêm ít nhất **10 test cases "Red Teaming"** (câu hỏi khó/tấn công) theo hướng dẫn trong `data/HARD_CASES_GUIDE.md`.

## 📐 Hướng dẫn chi tiết cho AI Agent

```
CONTEXT:
Bạn đang làm việc trong repo Lab14-AI-Evaluation-Benchmarking.
File cần implement: data/synthetic_gen.py và engine/retrieval_eval.py.

NHIỆM VỤ 1 - Implement data/synthetic_gen.py:
Sửa hàm generate_qa_from_text() để gọi OpenAI API (model gpt-4o-mini)
sinh ra các cặp QA thực tế từ tài liệu cho trước.

Mỗi item phải có cấu trúc JSON chính xác sau:
{
  "id": "case_XXX",          <- đánh số tăng dần, 3 chữ số
  "question": "...",         <- câu hỏi tự nhiên, rõ ràng
  "expected_answer": "...",  <- câu trả lời chuẩn từ tài liệu
  "context": "...",          <- đoạn văn bản gốc (max 500 ký tự)
  "expected_retrieval_ids": ["doc_001"],  <- ID tài liệu chứa đáp án
  "metadata": {
    "difficulty": "easy|medium|hard|adversarial",
    "type": "fact-check|reasoning|adversarial|out-of-scope",
    "category": "..."
  }
}

Phân bổ 50 cases theo tỉ lệ:
- 25 easy/medium (fact-check cơ bản)
- 15 hard (cần reasoning nhiều bước)
- 10 adversarial (Red Teaming): bao gồm
  * 3 câu "out-of-scope" (ngoài phạm vi tài liệu)
  * 3 câu "prompt injection" (hỏi Agent làm việc không liên quan)
  * 2 câu "ambiguous" (mơ hồ, thiếu thông tin)
  * 2 câu "conflicting" (thông tin mâu thuẫn nhau)

Sau khi generate xong, ghi tất cả vào data/golden_set.jsonl
(mỗi dòng là 1 JSON object).

NHIỆM VỤ 2 - Implement engine/retrieval_eval.py:
Hàm calculate_hit_rate() đã có logic đúng, chỉ cần thêm docstring đầy đủ.
Hàm calculate_mrr() đã có logic đúng, chỉ cần thêm docstring đầy đủ.

Implement hàm evaluate_batch() để:
1. Nhận vào dataset (List[Dict]) từ golden_set.jsonl
2. Với mỗi case, gọi calculate_hit_rate() và calculate_mrr()
   với expected_retrieval_ids và retrieved_ids (lấy từ agent response)
3. Tính avg_hit_rate và avg_mrr trên toàn bộ dataset
4. Trả về Dict: {"avg_hit_rate": float, "avg_mrr": float, "per_case": [...]}

REQUIREMENTS:
- Sử dụng thư viện: openai, python-dotenv, json, asyncio
- Load API key từ .env file (OPENAI_API_KEY)
- Code phải chạy được bằng lệnh: python data/synthetic_gen.py
- Không hardcode API key vào file code
```

## ⚠️ Điểm cần chú ý
- File `data/golden_set.jsonl` **phải có** trường `expected_retrieval_ids` — đây là trường bắt buộc để Người 3 tính được Hit Rate thực tế.
- Phải tạo ngay **1 file mock nhỏ** (`data/mock_golden_3cases.jsonl`) với 3 rows để gửi cho Người 3 test trước, không chờ đủ 50 cases.
- Tham khảo `data/HARD_CASES_GUIDE.md` để thiết kế các trường hợp khó.

---

---

# 👤 NGƯỜI 2 — AI Judge Engineer

## 📁 File phụ trách
| File | Trạng thái ban đầu | Nhiệm vụ |
|---|---|---|
| `engine/llm_judge.py` | Có skeleton (TODO) | **Implement hoàn toàn** |

## 🎯 Mục tiêu cụ thể
- [ ] Implement `evaluate_multi_judge()`: Gọi **ít nhất 2 model LLM khác nhau** (GPT-4o + Claude Haiku hoặc Gemini).
- [ ] Tính toán `agreement_rate` giữa 2 model.
- [ ] Viết **Conflict Resolution Logic**: Nếu 2 Judge lệch nhau > 1 điểm thì xử lý như thế nào.
- [ ] Implement `check_position_bias()`: Đổi thứ tự context A/B để kiểm tra Judge có bị thiên vị không.
- [ ] Viết unit test nhỏ để tự test module trước khi ráp vào `main.py`.

## 📐 Hướng dẫn chi tiết cho AI Agent

```
CONTEXT:
Bạn đang implement file engine/llm_judge.py trong repo Lab14-AI-Evaluation-Benchmarking.
File này chứa class LLMJudge - bộ não chấm điểm của hệ thống Evaluation.

NHIỆM VỤ - Implement class LLMJudge hoàn chỉnh:

CLASS STRUCTURE:
class LLMJudge:
    def __init__(self, models: list = ["gpt-4o", "claude-3-haiku-20240307"]):
        - Khởi tạo client OpenAI và Anthropic từ API Key trong .env
        - self.models = models
        - self.rubrics = {...}  (xem bên dưới)

RUBRICS (tiêu chí chấm điểm) phải có:
self.rubrics = {
    "accuracy": "Chấm 1-5: 5=Đúng hoàn toàn, 4=Đúng chính, 3=Một phần, 2=Phần lớn sai, 1=Hoàn toàn sai",
    "completeness": "Chấm 1-5: Câu trả lời có đủ thông tin cần thiết không?",
    "tone": "Chấm 1-5: Ngôn ngữ có chuyên nghiệp, phù hợp không?",
    "hallucination": "Chấm 1-5: 5=Không bịa, 1=Bịa hoàn toàn"
}

NHIỆM VỤ CHÍNH - evaluate_multi_judge():
async def evaluate_multi_judge(self, question, answer, ground_truth) -> Dict:
    1. Tạo prompt chấm điểm chuẩn từ rubrics
    2. Gọi Model A (OpenAI GPT-4o) và Model B (Anthropic Claude) song song bằng asyncio.gather()
    3. Parse điểm từ response (yêu cầu model trả về JSON: {"score": int, "reasoning": str})
    4. Tính final_score:
       - Nếu abs(score_a - score_b) <= 1: final_score = trung bình cộng
       - Nếu abs(score_a - score_b) > 1:  CONFLICT → gọi Model thứ 3 (gpt-4o-mini) làm trọng tài
         final_score = median(score_a, score_b, score_tiebreak)
    5. Tính agreement_rate: 1.0 nếu bằng nhau, 0.5 nếu lệch 1, 0.0 nếu lệch > 1
    6. Return:
       {
         "final_score": float,           # 1.0 - 5.0
         "agreement_rate": float,        # 0.0 - 1.0
         "individual_scores": {
           "gpt-4o": {"score": int, "reasoning": str},
           "claude": {"score": int, "reasoning": str}
         },
         "conflict_resolved": bool,      # True nếu có dùng tiebreaker
         "reasoning": str               # Giải thích ngắn gọn kết quả
       }

NHIỆM VỤ PHỤ - check_position_bias():
async def check_position_bias(self, response_a, response_b) -> Dict:
    - Gọi Judge 2 lần với thứ tự A,B và sau đó B,A
    - So sánh xem Judge có đổi điểm khi đổi thứ tự không
    - Return: {"bias_detected": bool, "score_order_AB": float, "score_order_BA": float}

REQUIREMENTS:
- Cài thêm anthropic vào requirements.txt nếu cần
- Load key từ .env: OPENAI_API_KEY, ANTHROPIC_API_KEY
- Tất cả I/O phải là async
- Viết __main__ block để self-test: python engine/llm_judge.py
  Test case mẫu:
    question = "Làm thế nào đặt lại mật khẩu?"
    answer = "Vào Settings rồi bấm Reset Password."
    ground_truth = "Vào Cài đặt → Bảo mật → Đổi mật khẩu."
  Kỳ vọng: final_score >= 3.0
```

## ⚠️ Điểm cần chú ý
- **ĐIỂM LIỆT:** Nếu chỉ gọi 1 model, phần nhóm bị giới hạn 30/60đ. Phải có đúng 2+ model thật.
- Thêm `anthropic>=0.20.0` vào `requirements.txt` nếu dùng Claude API.
- Prompt gửi cho Judge phải **yêu cầu trả về JSON**, không phải text tự do — dễ parse hơn.
- Chú ý xử lý exception khi API timeout hoặc rate limit.

---

---

# 👤 NGƯỜI 3 — Backend & Performance Engineer

## 📁 File phụ trách
| File | Trạng thái ban đầu | Nhiệm vụ |
|---|---|---|
| `engine/runner.py` | Có skeleton (TODO) | **Nâng cấp hoàn toàn** |
| `agent/main_agent.py` | Placeholder | **Nâng cấp thành Agent thật** |
| `main.py` | Có skeleton | **Hoàn thiện & ráp nối tất cả** |

## 🎯 Mục tiêu cụ thể
- [ ] Nâng cấp `agent/main_agent.py` thành RAG Agent thực tế (gọi LLM thật).
- [ ] Nâng cấp `engine/runner.py`: Thêm **Cost Tracker** (đếm token + tính USD).
- [ ] Implement `main.py` hoàn chỉnh: Ráp nối Data (Người 1) + Judge (Người 2) + Retrieval (Người 1).
- [ ] Đảm bảo toàn bộ pipeline chạy **50 cases dưới 2 phút** nhờ Async.
- [ ] Sinh ra đúng format `reports/summary.json` và `reports/benchmark_results.json`.

## 📐 Hướng dẫn chi tiết cho AI Agent

```
CONTEXT:
Bạn đang implement 3 file cốt lõi trong repo Lab14-AI-Evaluation-Benchmarking.
Đây là phần quan trọng nhất: điều phối toàn bộ pipeline chạy evaluation.

--- FILE 1: agent/main_agent.py ---
Nâng cấp class MainAgent từ placeholder thành RAG Agent thực tế:

class MainAgent:
    def __init__(self):
        - Khởi tạo OpenAI client
        - Khởi tạo danh sách documents (có thể dùng in-memory list hoặc load từ file)
        - self.name = "SupportAgent-v1" (hoặc v2 nếu đây là phiên bản mới hơn)

    async def query(self, question: str) -> Dict:
        Quy trình:
        1. RETRIEVAL: Tìm kiếm top-3 documents liên quan (dùng simple keyword matching
           hoặc cosine similarity nếu có embedding). Ghi lại retrieved_ids.
        2. BUILD CONTEXT: Ghép nội dung các docs lại thành context string.
        3. GENERATION: Gọi gpt-4o-mini với system prompt + context + question.
        4. Track tokens: Lấy usage từ response.usage
        5. Return:
           {
             "answer": str,
             "contexts": [str, str, str],          # top-3 chunks
             "retrieved_ids": ["doc_001", ...],    # ID tương ứng
             "metadata": {
               "model": "gpt-4o-mini",
               "tokens_used": int,                 # prompt + completion tokens
               "sources": [str]
             }
           }

--- FILE 2: engine/runner.py ---
Nâng cấp class BenchmarkRunner:

class BenchmarkRunner:
    def __init__(self, agent, evaluator, judge):
        - self.cost_tracker = {"total_tokens": 0, "total_cost_usd": 0.0}
        - Giá tham chiếu (gpt-4o-mini): $0.15/1M input tokens, $0.60/1M output tokens

    async def run_single_test(self, test_case) -> Dict:
        - Gọi agent.query()
        - Cộng dồn token vào self.cost_tracker
        - Gọi evaluator.score() và judge.evaluate_multi_judge() song song:
          ragas_result, judge_result = await asyncio.gather(
              evaluator.score(test_case, response),
              judge.evaluate_multi_judge(q, answer, gt)
          )
        - Tính latency
        - Return kết quả đầy đủ

    async def run_all(self, dataset, batch_size=5) -> List[Dict]:
        - Chạy theo từng batch (5 cases/lần) để tránh rate limit
        - Dùng tqdm để hiển thị progress bar
        - Sau khi xong, in ra báo cáo cost:
          print(f"💰 Tổng chi phí: ${self.cost_tracker['total_cost_usd']:.4f}")
          print(f"🔢 Tổng tokens: {self.cost_tracker['total_tokens']:,}")

--- FILE 3: main.py ---
Hoàn thiện hàm main() để:

1. Chạy V1 (Agent gốc, prompt cơ bản):
   v1_results, v1_summary = await run_benchmark_with_results("Agent_V1_Base")

2. Thay đổi nhỏ ở system prompt của Agent để tạo V2:
   (ví dụ: thêm "Chỉ trả lời dựa trên context được cung cấp, không bịa thêm.")
   v2_results, v2_summary = await run_benchmark_with_results("Agent_V2_Optimized")

3. Tính delta và điền đủ vào summary.json:
   {
     "metadata": {...},
     "metrics": {
       "avg_score": ...,
       "hit_rate": ...,
       "mrr": ...,
       "agreement_rate": ...,
       "cost_usd": ...,
       "total_tokens": ...
     },
     "regression": {
       "v1_avg_score": ...,
       "v2_avg_score": ...,
       "delta": ...,
       "decision": "APPROVE" hoặc "ROLLBACK"
     }
   }

4. Lưu CÙNG LÚC 2 file:
   - reports/summary.json    (format ở trên)
   - reports/benchmark_results.json (toàn bộ v2_results list)

REQUIREMENTS:
- Phải chạy được: python main.py (không lỗi)
- Thời gian chạy < 2 phút cho 50 cases
- In ra progress bar (dùng tqdm)
- Xử lý exception: nếu 1 case lỗi thì skip và log, không crash toàn bộ
```

## ⚠️ Điểm cần chú ý
- **Ngay từ đầu:** Dùng file `data/mock_golden_3cases.jsonl` (do Người 1 cung cấp) để test `main.py` trước khi có đủ 50 cases.
- Để tạo phiên bản V1 và V2, **không cần tạo 2 class agent riêng biệt** — chỉ cần thay đổi system prompt là đủ để tạo ra sự khác biệt thống kê.
- Import module từ Người 2: `from engine.llm_judge import LLMJudge` — phối hợp sớm để tránh xung đột interface.

---

---

# 👤 NGƯỜI 4 — DevOps & Release Gate Engineer

## 📁 File phụ trách
| File | Trạng thái ban đầu | Nhiệm vụ |
|---|---|---|
| `reports/summary.json` | Chưa có (do `main.py` sinh ra) | **Đọc & Validate** |
| `reports/benchmark_results.json` | Chưa có | **Đọc & Phân tích** |
| `check_lab.py` | Có sẵn, chạy được | **Chạy kiểm tra & nếu thiếu logic thì bổ sung** |
| *(Tạo mới)* `reports/regression_gate.py` | Chưa có | **Tạo mới** |

## 🎯 Mục tiêu cụ thể
- [ ] Tạo file `reports/regression_gate.py` với logic Release Gate tự động.
- [ ] Chạy `python check_lab.py` và đảm bảo tất cả checks đều **PASS** trước khi nộp.
- [ ] Bổ sung thêm Kiểm tra "mrr" và "cost_usd" vào `check_lab.py` nếu chưa có.
- [ ] Viết báo cáo chi phí: So sánh chi phí V1 vs V2, đề xuất cách tối ưu 30%.

## 📐 Hướng dẫn chi tiết cho AI Agent

```
CONTEXT:
Bạn đang làm việc trong repo Lab14-AI-Evaluation-Benchmarking.
File check_lab.py đã tồn tại và có logic cơ bản (kiểm tra file tồn tại,
kiểm tra hit_rate, agreement_rate trong summary.json).

NHIỆM VỤ 1 - Tạo file reports/regression_gate.py:

Script này đọc reports/summary.json và in ra quyết định RELEASE hay ROLLBACK
dựa trên các ngưỡng chất lượng cứng (hard thresholds).

THRESHOLDS (ngưỡng quyết định):
QUALITY_THRESHOLD = 3.5       # avg_score tối thiểu trên thang 5
HIT_RATE_THRESHOLD = 0.75     # ít nhất 75% câu hỏi tìm đúng tài liệu
AGREEMENT_THRESHOLD = 0.70    # ít nhất 70% 2 Judge đồng ý
COST_BUDGET_USD = 1.00        # không được tốn quá $1 cho 50 cases
DELTA_THRESHOLD = 0.0         # V2 phải >= V1 (không được giảm điểm)

LOGIC GATE (kiểm tra từng điều kiện):
def run_release_gate(summary_path="reports/summary.json") -> str:
    1. Load summary.json
    2. Kiểm tra tuần tự:
       ✅ avg_score >= QUALITY_THRESHOLD
       ✅ hit_rate >= HIT_RATE_THRESHOLD
       ✅ agreement_rate >= AGREEMENT_THRESHOLD
       ✅ cost_usd <= COST_BUDGET_USD
       ✅ delta >= DELTA_THRESHOLD
    3. Nếu TẤT CẢ ✅: print "🚀 DECISION: APPROVE — Ready for release"
       Nếu CÓ ✅ THẤT BẠI:
         - In ra từng điều kiện bị fail
         - print "🔴 DECISION: ROLLBACK — Do not release"
    4. Lưu kết quả vào reports/gate_result.json:
       {
         "decision": "APPROVE" | "ROLLBACK",
         "checks": {
           "quality": {"pass": bool, "value": float, "threshold": float},
           "hit_rate": {"pass": bool, "value": float, "threshold": float},
           ...
         },
         "timestamp": "..."
       }
    5. Return "APPROVE" hoặc "ROLLBACK"

NHIỆM VỤ 2 - Bổ sung check_lab.py:
Đọc check_lab.py hiện tại và thêm vào phần EXPERT CHECKS:
- Kiểm tra "mrr" có trong metrics không
- Kiểm tra "cost_usd" có trong metrics không
- Kiểm tra "regression" section có trong summary không
- Nếu thiếu: in ra cảnh báo ⚠️ (không cần fail, chỉ warn)

NHIỆM VỤ 3 - Viết tài liệu phân tích chi phí:
Đọc reports/summary.json (hoặc dùng mock data nếu chưa có)
và tính toán:
- Chi phí/case = total_cost_usd / total_cases
- Chi phí cho 1000 cases = chi phí/case * 1000
- Đề xuất ít nhất 2 cách giảm 30% chi phí (ví dụ: cache, dùng model nhỏ hơn cho Judge)
Ghi vào reports/cost_analysis.md

MOCK DATA để test (dùng khi chưa có summary.json thật):
Tạo file reports/mock_summary.json với giá trị cứng để test logic gate trước.
```

## ⚠️ Điểm cần chú ý
- **Chạy `check_lab.py` thường xuyên** trong quá trình develop — đây là script chấm tự động, nếu lỗi sẽ bị trừ 5 điểm.
- Không cần chờ Người 1-2-3 xong mới làm được — tự tạo `mock_summary.json` với giá trị giả để test Logic Gate trước.
- Decision "APPROVE" phải khớp với decision trong file `summary.json` mà Người 3 tạo ra (cần sync lại ở bước Integration).

---

---

# 👤 NGƯỜI 5 — Analyst, Project Lead & Documentation

## 📁 File phụ trách
| File | Trạng thái ban đầu | Nhiệm vụ |
|---|---|---|
| `analysis/failure_analysis.md` | Có template sẵn | **Điền đầy đủ nội dung thật** |
| `analysis/reflections/reflection_[Tên_TV1].md` | Chưa có | **Nhắc các thành viên tự viết** |
| `analysis/reflections/reflection_[Tên_TV2].md` | Chưa có | Tương tự |
| `analysis/reflections/reflection_[Tên_TV3].md` | Chưa có | Tương tự |
| `analysis/reflections/reflection_[Tên_TV4].md` | Chưa có | Tương tự |
| `analysis/reflections/reflection_[Tên_TV5].md` | Chưa có | **Tự viết** |
| `README.md` | Có sẵn | **Cập nhật hướng dẫn chạy nếu cần** |

## 🎯 Mục tiêu cụ thể
- [ ] Điều phối nhóm theo mốc thời gian dưới đây.
- [ ] Sau khi có `reports/benchmark_results.json` thật: Điền đầy đủ `analysis/failure_analysis.md`.
- [ ] Thực hiện phân tích **"5 Whys"** cho ít nhất 3 case fail nặng nhất.
- [ ] Thu thập và merge 5 file reflection vào thư mục `analysis/reflections/`.
- [ ] Chạy `python check_lab.py` lần cuối và xác nhận `🚀 Bài lab đã sẵn sàng`.

## 📐 Hướng dẫn chi tiết cho AI Agent

```
CONTEXT:
Bạn đang hoàn thiện tài liệu phân tích cho repo Lab14-AI-Evaluation-Benchmarking.
File cần điền: analysis/failure_analysis.md (template đã có sẵn).
Input chính: reports/benchmark_results.json (do Người 3 tạo ra khi chạy main.py)

NHIỆM VỤ 1 - Phân tích dữ liệu từ benchmark_results.json:
Đọc toàn bộ file benchmarks_results.json và tính:
1. Tổng số cases / số Pass (score >= 3.0) / số Fail (score < 3.0)
2. Tỉ lệ Pass/Fail
3. RAGAS metrics trung bình (faithfulness, relevancy)
4. Điểm LLM-Judge trung bình (final_score)
5. Chọn 3 case có final_score THẤP NHẤT để phân tích sâu

NHIỆM VỤ 2 - Điền vào analysis/failure_analysis.md:
Template đã có sẵn, điền vào phần dữ liệu thật:

Section 1. Tổng quan Benchmark:
- Điền số liệu tính được ở Nhiệm vụ 1

Section 2. Phân nhóm lỗi (Failure Clustering):
- Đọc danh sách các case fail
- Phân loại theo pattern:
  * Hallucination: Agent bịa thông tin không có trong context
  * Incomplete: Câu trả lời đúng nhưng thiếu thông tin quan trọng
  * Off-topic: Agent trả lời khi đó không phải thông tin từ tài liệu
  * Irrelevant Retrieval: Retriever lấy sai documents
- Điền vào bảng: Nhóm lỗi | Số lượng | Nguyên nhân dự kiến

Section 3. Phân tích 5 Whys:
Với MỖI case trong 3 case tệ nhất, thực hiện:
  Case #X: Trích dẫn question + agent_response thật từ JSON
  Symptom: Agent trả lời sai/thiếu/bịa về...
  Why 1: LLM nhận được context gì?
  Why 2: Context đó có đủ/chính xác không?
  Why 3: Retriever có lấy đúng document không? (kiểm tra hit_rate của case đó)
  Why 4: Nếu retriever sai - tại sao? Chunking? Embedding? Query?
  Why 5: (Root Cause) Vấn đề gốc rễ ở tầng nào của hệ thống?
  Root Cause: [1 câu tóm tắt ngắn gọn nhất]

Section 4. Kế hoạch cải tiến:
Dựa trên Root Cause, đề xuất ít nhất 3 action items cụ thể có thể thực hiện được.

NHIỆM VỤ 3 - Tạo thư mục reflections:
Tạo thư mục analysis/reflections/ và tạo template file cho mỗi thành viên:

# Reflection — [Tên Sinh Viên]

## 1. Tôi đã làm gì trong bài lab này?
(Mô tả cụ thể module/code của bạn)

## 2. Kỹ thuật tôi học được
(Ít nhất 2 concept: VD: MRR, Async, Cohen's Kappa...)

## 3. Khó khăn gặp phải và cách giải quyết
(Ít nhất 1 vấn đề kỹ thuật thật sự)

## 4. Nếu làm lại, tôi sẽ thay đổi gì?
(Trade-off về chi phí, chất lượng, tốc độ...)

Gửi template này cho 4 thành viên còn lại tự điền.

LƯUÝ: Nếu chưa có file benchmark_results.json thật,
hãy tạo mock data với 10 cases giả để viết sườn báo cáo trước.
Khi có data thật thì thay số vào.
```

## ⚠️ Điểm cần chú ý
- Phân tích "5 Whys" phải trích dẫn **dữ liệu thật từ JSON** — giám khảo sẽ không chấp nhận các con số bịa.
- Phải tạo thư mục `analysis/reflections/` và có đủ 5 file reflection cá nhân mỗi người trước khi nộp.
- Đây là role "Leader" — bạn chịu trách nhiệm kiểm tra nộp bài cuối cùng và chạy `check_lab.py`.

---

---

## ⏱️ Mốc thời gian bắt buộc (Timeline cho 4 giờ)

| Thời điểm | Milestone | Người thực hiện |
|---|---|---|
| **T+0:00** | Họp nhanh 10 phút: xác nhận Data Contract, chia branch Git | Tất cả |
| **T+0:10** | Tản ra code độc lập trên branch riêng | Tất cả |
| **T+0:30** | Người 1 tạo xong `mock_golden_3cases.jsonl` → gửi Slack/nhóm | Người 1 |
| **T+1:00** | Người 2 self-test xong `llm_judge.py` với `__main__` block | Người 2 |
| **T+1:00** | Người 3 chạy được `main.py` với mock data (3 cases) | Người 3 |
| **T+1:30** | **⚡ INTEGRATION SPRINT:** Bộ ba 1+2+3 ngồi chung ráp code | Người 1+2+3 |
| **T+2:00** | `python main.py` chạy thành công với 50 cases thật, sinh ra `reports/` | Người 1+2+3 |
| **T+2:15** | Người 4 chạy `regression_gate.py` với data thật | Người 4 |
| **T+2:15** | Người 5 bắt đầu điền `failure_analysis.md` với số liệu thật | Người 5 |
| **T+3:00** | Tất cả code xong, mỗi người viết `reflection_[Tên].md` cá nhân | Tất cả |
| **T+3:30** | Người 5 merge tất cả vào `main`, chạy `check_lab.py` lần cuối | Người 5 |
| **T+4:00** | 🎉 Nộp bài | Người 5 (Leader) |

---

## 📁 Cấu trúc cuối cùng khi nộp bài

```
Lab14-AI-Evaluation-Benchmarking/
├── agent/
│   └── main_agent.py          ✅ (Người 3)
├── data/
│   ├── synthetic_gen.py       ✅ (Người 1)
│   ├── golden_set.jsonl       ✅ (Người 1 - sinh ra, KHÔNG commit)
│   └── HARD_CASES_GUIDE.md
├── engine/
│   ├── llm_judge.py           ✅ (Người 2)
│   ├── retrieval_eval.py      ✅ (Người 1)
│   └── runner.py              ✅ (Người 3)
├── reports/
│   ├── summary.json           ✅ (Người 3 sinh ra, Người 4 validate)
│   ├── benchmark_results.json ✅ (Người 3 sinh ra)
│   ├── regression_gate.py     ✅ (Người 4)
│   └── cost_analysis.md       ✅ (Người 4)
├── analysis/
│   ├── failure_analysis.md    ✅ (Người 5)
│   └── reflections/
│       ├── reflection_[TV1].md ✅
│       ├── reflection_[TV2].md ✅
│       ├── reflection_[TV3].md ✅
│       ├── reflection_[TV4].md ✅
│       └── reflection_[TV5].md ✅
├── main.py                    ✅ (Người 3)
├── check_lab.py               ✅ (Người 4 bổ sung)
├── requirements.txt           ✅ (Người 2/3 cập nhật nếu thêm thư viện)
├── .env                       ❌ KHÔNG commit
└── README.md
```

---

## 🚨 Checklist nộp bài (chạy lần cuối)

```bash
# Bước 1: Tạo data
python data/synthetic_gen.py

# Bước 2: Chạy benchmark
python main.py

# Bước 3: Kiểm tra định dạng
python check_lab.py

# Bước 4: Chạy Release Gate
python reports/regression_gate.py

# Bước 5: Xác nhận GIT không có file .env
git status
```

**Tất cả checks phải hiện `✅` trước khi nộp bài.**
