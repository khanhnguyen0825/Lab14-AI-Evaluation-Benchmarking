import asyncio
import json
import os
import time

from engine.runner import BenchmarkRunner
from agent.main_agent import MainAgent
from engine.llm_judge import LLMJudge
from engine.retrieval_eval import RetrievalEvaluator

class ExpertEvaluator:
    """Bridge evaluator that combines simple answer quality and retrieval metrics."""

    def __init__(self):
        self.retrieval_evaluator = RetrievalEvaluator(default_top_k=3)

    @staticmethod
    def _text_overlap_ratio(a: str, b: str) -> float:
        a_tokens = set((a or "").lower().split())
        b_tokens = set((b or "").lower().split())
        if not b_tokens:
            return 0.0
        return len(a_tokens.intersection(b_tokens)) / len(b_tokens)

    async def score(self, case, resp):
        expected_ids = case.get("expected_retrieval_ids", [])
        retrieved_ids = resp.get("retrieved_ids", [])

        hit_rate = self.retrieval_evaluator.calculate_hit_rate(expected_ids, retrieved_ids)
        mrr = self.retrieval_evaluator.calculate_mrr(expected_ids, retrieved_ids)

        expected_answer = case.get("expected_answer", "")
        model_answer = resp.get("answer", "")
        overlap = self._text_overlap_ratio(model_answer, expected_answer)

        faithfulness = round(min(1.0, 0.5 + overlap * 0.5), 4)
        relevancy = round(min(1.0, 0.4 + overlap * 0.6), 4)

        return {
            "faithfulness": faithfulness,
            "relevancy": relevancy,
            "retrieval": {"hit_rate": hit_rate, "mrr": mrr},
        }


def load_dataset() -> list[dict]:
    candidates = ["data/golden_set.jsonl", "data/mock_golden_3cases.jsonl"]
    for path in candidates:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                dataset = [json.loads(line) for line in f if line.strip()]
            if dataset:
                print(f"Su dung dataset: {path} ({len(dataset)} cases)")
                return dataset
    return []


def build_documents_from_dataset(dataset: list[dict]) -> list[dict]:
    """Create retrieval documents aligned with expected_retrieval_ids in dataset."""
    doc_map: dict[str, dict] = {}

    for case in dataset:
        context = (case.get("context") or "").strip()
        expected_ids = case.get("expected_retrieval_ids", []) or []
        meta = case.get("metadata", {}) or {}
        source_doc = meta.get("source_doc", "dataset")

        for doc_id in expected_ids:
            if not doc_id:
                continue
            if doc_id not in doc_map:
                doc_map[doc_id] = {
                    "id": doc_id,
                    "source": source_doc,
                    "content": context,
                }
            elif context and context not in doc_map[doc_id]["content"]:
                doc_map[doc_id]["content"] += f"\n\n{context}"

    # Fallback: if expected ids are missing, create docs from case IDs to keep agent functional.
    if not doc_map:
        for idx, case in enumerate(dataset, start=1):
            context = (case.get("context") or "").strip()
            if not context:
                continue
            fallback_id = case.get("id", f"case_doc_{idx:03d}")
            doc_map[fallback_id] = {
                "id": fallback_id,
                "source": "dataset_fallback",
                "content": context,
            }

    return list(doc_map.values())


def summarize_results(agent_version: str, results: list[dict], runner: BenchmarkRunner) -> dict:
    total = len(results)
    if total == 0:
        return {
            "metadata": {
                "version": agent_version,
                "total": 0,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "metrics": {
                "avg_score": 0.0,
                "hit_rate": 0.0,
                "mrr": 0.0,
                "agreement_rate": 0.0,
                "cost_usd": 0.0,
                "total_tokens": 0,
            },
        }

    avg_score = sum(r["judge"].get("final_score", 0.0) for r in results) / total
    avg_hit_rate = sum(r["ragas"]["retrieval"].get("hit_rate", 0.0) for r in results) / total
    avg_mrr = sum(r["ragas"]["retrieval"].get("mrr", 0.0) for r in results) / total
    avg_agreement = sum(r["judge"].get("agreement_rate", 0.0) for r in results) / total

    return {
        "metadata": {
            "version": agent_version,
            "total": total,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "metrics": {
            "avg_score": round(avg_score, 4),
            "hit_rate": round(avg_hit_rate, 4),
            "mrr": round(avg_mrr, 4),
            "agreement_rate": round(avg_agreement, 4),
            "cost_usd": round(runner.cost_tracker["total_cost_usd"], 6),
            "total_tokens": int(runner.cost_tracker["total_tokens"]),
        },
    }


async def run_benchmark_with_results(
    agent_version: str,
    system_prompt: str,
    dataset: list[dict],
    documents: list[dict],
    batch_size: int,
    max_output_tokens: int,
):
    print(f"🚀 Khởi động Benchmark cho {agent_version}...")

    if not dataset:
        print("❌ Dataset rỗng. Hãy tạo data/golden_set.jsonl hoặc data/mock_golden_3cases.jsonl.")
        return None, None

    agent = MainAgent(
        system_prompt=system_prompt,
        name=agent_version,
        documents=documents,
        max_output_tokens=max_output_tokens,
    )
    evaluator = ExpertEvaluator()
    # Faster pair of real judges to improve throughput while keeping multi-model evaluation.
    judge = LLMJudge(models=["gpt-4o-mini", "claude-haiku-4-5"])
    runner = BenchmarkRunner(agent, evaluator, judge)

    results = await runner.run_all(dataset, batch_size=batch_size)
    summary = summarize_results(agent_version, results, runner)
    return results, summary


async def main():
    dataset = load_dataset()
    if not dataset:
        print("❌ Khong tim thay dataset hop le trong data/golden_set.jsonl hoac data/mock_golden_3cases.jsonl")
        return

    documents = build_documents_from_dataset(dataset)
    print(f"Da tao kho tai lieu retrieval: {len(documents)} documents")

    batch_size = int(os.getenv("BENCH_BATCH_SIZE", "10"))

    v1_prompt = (
        "Ban la tro ly ho tro. Tra loi ngan gon, khong can giai thich chi tiet."
    )
    v2_prompt = (
        "Ban la tro ly ho tro. Chi duoc tra loi dua tren context duoc cung cap, "
        "khong bịa them thong tin. Neu context khong du, hay noi ro va trich dan id tai lieu."
    )

    v1_results, v1_summary = await run_benchmark_with_results(
        "Agent_V1_Base",
        v1_prompt,
        dataset,
        documents,
        batch_size,
        90,
    )
    v2_results, v2_summary = await run_benchmark_with_results(
        "Agent_V2_Optimized",
        v2_prompt,
        dataset,
        documents,
        batch_size,
        180,
    )

    if not v1_summary or not v2_summary or v2_results is None or v1_results is None:
        print("❌ Khong the hoan tat benchmark.")
        return

    print("\n📊 --- KẾT QUẢ SO SÁNH (REGRESSION) ---")
    delta = v2_summary["metrics"]["avg_score"] - v1_summary["metrics"]["avg_score"]
    decision = "APPROVE" if delta >= 0 else "ROLLBACK"

    print(f"V1 Score: {v1_summary['metrics']['avg_score']}")
    print(f"V2 Score: {v2_summary['metrics']['avg_score']}")
    print(f"Delta: {'+' if delta >= 0 else ''}{delta:.2f}")

    final_summary = {
        "metadata": v2_summary["metadata"],
        "metrics": v2_summary["metrics"],
        "regression": {
            "v1_avg_score": round(v1_summary["metrics"]["avg_score"], 4),
            "v2_avg_score": round(v2_summary["metrics"]["avg_score"], 4),
            "delta": round(delta, 4),
            "decision": decision,
        },
    }

    os.makedirs("reports", exist_ok=True)
    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump(final_summary, f, ensure_ascii=False, indent=2)

    with open("reports/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(v2_results, f, ensure_ascii=False, indent=2)

    print(f"Quyet dinh Regression: {decision}")
    print("Da luu reports/summary.json va reports/benchmark_results.json")

if __name__ == "__main__":
    asyncio.run(main())
