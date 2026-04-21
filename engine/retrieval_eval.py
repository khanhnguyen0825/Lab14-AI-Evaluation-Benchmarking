"""
retrieval_eval.py — Người 1: Data & Retrieval Engineer
Đánh giá chất lượng Retrieval stage của RAG pipeline.
Các metrics: Hit Rate @ K, MRR (Mean Reciprocal Rank).
"""

from typing import List, Dict, Optional
import json


class RetrievalEvaluator:
    """
    Đánh giá chất lượng Retrieval của hệ thống RAG bằng các chỉ số:
    - Hit Rate @ K: Tỉ lệ truy vấn tìm được ít nhất 1 document đúng trong top K kết quả.
    - MRR (Mean Reciprocal Rank): Đo mức độ document đúng xuất hiện cao hay thấp trong ranking.

    Giải thích trực quan:
        Hit Rate = 0.8  → 80% câu hỏi có document đúng trong top-K
        MRR      = 0.6  → Trung bình document đúng ở vị trí 1/0.6 ≈ 1.67 (gần đầu danh sách)
        MRR      = 0.2  → Trung bình document đúng ở vị trí 5 (gần cuối, retriever kém)
    """

    def __init__(self, default_top_k: int = 3):
        """
        Args:
            default_top_k: Số lượng kết quả top-K mặc định để tính Hit Rate.
                           Thông thường dùng K=3 hoặc K=5.
        """
        self.default_top_k = default_top_k

    # ------------------------------------------------------------------
    # 📐 CORE METRICS
    # ------------------------------------------------------------------

    def calculate_hit_rate(
        self,
        expected_ids: List[str],
        retrieved_ids: List[str],
        top_k: Optional[int] = None,
    ) -> float:
        """
        Tính Hit Rate @ K: Kiểm tra xem ít nhất 1 expected document có nằm trong
        top K kết quả retrieved không.

        Args:
            expected_ids:  Danh sách ID tài liệu chứa đáp án đúng (Ground Truth).
            retrieved_ids: Danh sách ID tài liệu mà Retriever trả về (theo thứ tự rank).
            top_k:         Chỉ xét K kết quả đầu tiên. Mặc định dùng self.default_top_k.

        Returns:
            1.0 nếu HIT (tìm thấy), 0.0 nếu MISS (không tìm thấy).

        Example:
            expected_ids  = ["doc_001"]
            retrieved_ids = ["doc_003", "doc_001", "doc_007"]   → HIT → 1.0
            retrieved_ids = ["doc_003", "doc_005", "doc_007"]   → MISS → 0.0
        """
        if not expected_ids or not retrieved_ids:
            return 0.0

        k = top_k if top_k is not None else self.default_top_k
        top_retrieved = set(retrieved_ids[:k])
        hit = any(doc_id in top_retrieved for doc_id in expected_ids)
        return 1.0 if hit else 0.0

    def calculate_mrr(
        self,
        expected_ids: List[str],
        retrieved_ids: List[str],
    ) -> float:
        """
        Tính MRR (Mean Reciprocal Rank) cho một truy vấn đơn lẻ.

        MRR = 1 / (vị trí đầu tiên tìm thấy document đúng, 1-indexed)
        Nếu không tìm thấy → MRR = 0.0

        Args:
            expected_ids:  Danh sách ID tài liệu đúng (Ground Truth).
            retrieved_ids: Danh sách ID tài liệu trả về (theo thứ tự rank từ 1).

        Returns:
            float trong khoảng [0.0, 1.0]

        Example:
            expected_ids  = ["doc_001"]
            retrieved_ids = ["doc_001", "doc_003"]   → vị trí 1 → MRR = 1/1 = 1.0
            retrieved_ids = ["doc_003", "doc_001"]   → vị trí 2 → MRR = 1/2 = 0.5
            retrieved_ids = ["doc_003", "doc_005"]   → không tìm thấy → MRR = 0.0
        """
        if not expected_ids or not retrieved_ids:
            return 0.0

        for rank, doc_id in enumerate(retrieved_ids, start=1):
            if doc_id in expected_ids:
                return 1.0 / rank
        return 0.0

    # ------------------------------------------------------------------
    # 📦 BATCH EVALUATION
    # ------------------------------------------------------------------

    async def evaluate_batch(
        self,
        dataset: List[Dict],
        top_k: Optional[int] = None,
    ) -> Dict:
        """
        Chạy Retrieval Evaluation cho toàn bộ dataset.

        Mỗi item trong dataset cần có:
            - "expected_retrieval_ids": List[str]  — Ground Truth document IDs
            - "retrieved_ids":          List[str]  — Kết quả từ Agent (được gắn sau khi chạy query)

        Args:
            dataset: Danh sách các test case đã có kết quả retrieved_ids từ Agent.
            top_k:   Ghi đè default_top_k nếu cần.

        Returns:
            Dict gồm:
                - avg_hit_rate:  float   — Hit Rate trung bình toàn bộ dataset
                - avg_mrr:       float   — MRR trung bình toàn bộ dataset
                - total_cases:   int     — Tổng số cases đã eval
                - hit_cases:     int     — Số cases có HIT
                - miss_cases:    int     — Số cases MISS
                - per_case:      List    — Chi tiết từng case
        """
        k = top_k if top_k is not None else self.default_top_k
        per_case_results = []
        hit_count = 0

        for case in dataset:
            case_id = case.get("id", "unknown")
            expected = case.get("expected_retrieval_ids", [])
            retrieved = case.get("retrieved_ids", [])

            hit_rate = self.calculate_hit_rate(expected, retrieved, top_k=k)
            mrr = self.calculate_mrr(expected, retrieved)

            if hit_rate > 0:
                hit_count += 1

            per_case_results.append({
                "case_id": case_id,
                "hit_rate": hit_rate,
                "mrr": mrr,
                "expected_ids": expected,
                "retrieved_ids": retrieved,
                "top_k": k,
                "is_hit": hit_rate > 0,
            })

        total = len(dataset)
        avg_hit = sum(r["hit_rate"] for r in per_case_results) / total if total else 0.0
        avg_mrr = sum(r["mrr"] for r in per_case_results) / total if total else 0.0

        return {
            "avg_hit_rate": round(avg_hit, 4),
            "avg_mrr": round(avg_mrr, 4),
            "total_cases": total,
            "hit_cases": hit_count,
            "miss_cases": total - hit_count,
            "top_k_used": k,
            "per_case": per_case_results,
        }

    # ------------------------------------------------------------------
    # 📊 REPORTING
    # ------------------------------------------------------------------

    def print_summary(self, eval_result: Dict) -> None:
        """In bảng tóm tắt kết quả Retrieval Evaluation ra console."""
        print("\n" + "=" * 50)
        print(" RETRIEVAL EVALUATION SUMMARY")
        print("=" * 50)
        print(f"  Total cases  : {eval_result['total_cases']}")
        print(f"  Top-K used   : {eval_result['top_k_used']}")
        print(f"  Hit Rate @{eval_result['top_k_used']}  : {eval_result['avg_hit_rate'] * 100:.1f}%")
        print(f"  MRR          : {eval_result['avg_mrr']:.4f}")
        print(f"  Hits / Misses: {eval_result['hit_cases']} / {eval_result['miss_cases']}")

        if eval_result["avg_hit_rate"] >= 0.80:
            verdict = " EXCELLENT — Retriever hoạt động tốt"
        elif eval_result["avg_hit_rate"] >= 0.60:
            verdict = " ACCEPTABLE — Cần cải thiện"
        else:
            verdict = " POOR — Retriever cần được tối ưu gấp"
        print(f"  Verdict      : {verdict}")
        print("=" * 50)

        # In top-5 cases bị MISS để dễ debug
        misses = [c for c in eval_result["per_case"] if not c["is_hit"]]
        if misses:
            print(f"\n Top MISS cases (hiển thị tối đa 5):")
            for case in misses[:5]:
                print(f"  - {case['case_id']}")
                print(f"    Expected : {case['expected_ids']}")
                print(f"    Retrieved: {case['retrieved_ids'][:3]}")


# ============================================================
# 🧪 SELF-TEST — chạy: python engine/retrieval_eval.py
# ============================================================

if __name__ == "__main__":
    import asyncio
    import sys

    # Fix Windows console encoding
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    async def run_tests():
        evaluator = RetrievalEvaluator(default_top_k=3)

        print("[TEST] Unit Test: calculate_hit_rate()")
        assert evaluator.calculate_hit_rate(["doc_001"], ["doc_001", "doc_002"]) == 1.0, "Test 1 FAIL"
        assert evaluator.calculate_hit_rate(["doc_001"], ["doc_002", "doc_003"]) == 0.0, "Test 2 FAIL"
        assert evaluator.calculate_hit_rate(["doc_001"], ["doc_002", "doc_003", "doc_001"]) == 1.0, "Test 3 FAIL"
        assert evaluator.calculate_hit_rate(["doc_001"], ["doc_002", "doc_001"], top_k=1) == 0.0, "Test 4 FAIL (top_k=1)"
        assert evaluator.calculate_hit_rate([], ["doc_001"]) == 0.0, "Test 5 FAIL (empty expected)"
        print("  [OK] Tat ca Hit Rate tests PASS")

        print("\n[TEST] Unit Test: calculate_mrr()")
        assert evaluator.calculate_mrr(["doc_001"], ["doc_001", "doc_002"]) == 1.0, "MRR Test 1 FAIL"
        assert evaluator.calculate_mrr(["doc_001"], ["doc_002", "doc_001"]) == 0.5, "MRR Test 2 FAIL"
        assert evaluator.calculate_mrr(["doc_001"], ["doc_002", "doc_003", "doc_001"]) == _approx(1/3), "MRR Test 3 FAIL"
        assert evaluator.calculate_mrr(["doc_001"], ["doc_002", "doc_003"]) == 0.0, "MRR Test 4 FAIL"
        print("  [OK] Tat ca MRR tests PASS")

        print("\n[TEST] Integration Test: evaluate_batch()")
        mock_dataset = [
            {
                "id": "case_001",
                "expected_retrieval_ids": ["doc_001"],
                "retrieved_ids": ["doc_001", "doc_002", "doc_003"],
            },
            {
                "id": "case_002",
                "expected_retrieval_ids": ["doc_004"],
                "retrieved_ids": ["doc_001", "doc_002", "doc_003"],
            },
            {
                "id": "case_003",
                "expected_retrieval_ids": ["doc_002"],
                "retrieved_ids": ["doc_001", "doc_002", "doc_003"],
            },
        ]
        result = await evaluator.evaluate_batch(mock_dataset)
        assert result["total_cases"] == 3
        assert result["hit_cases"] == 2       # case_001 va case_003 HIT
        assert result["miss_cases"] == 1      # case_002 MISS
        assert result["avg_hit_rate"] == round(2/3, 4)
        evaluator.print_summary(result)
        print("  [OK] evaluate_batch() PASS")
        print("\n=== ALL TESTS PASSED ===")

    def _approx(val, rel=1e-6):
        class _Approx:
            def __eq__(self, other): return abs(other - val) < rel
        return _Approx()

    asyncio.run(run_tests())
