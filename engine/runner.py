import asyncio
import time
from typing import List, Dict
from tqdm import tqdm

class BenchmarkRunner:
    INPUT_PRICE_PER_1M = 0.15
    OUTPUT_PRICE_PER_1M = 0.60

    def __init__(self, agent, evaluator, judge):
        self.agent = agent
        self.evaluator = evaluator
        self.judge = judge
        self.cost_tracker = {"total_tokens": 0, "total_cost_usd": 0.0}

    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        input_cost = (prompt_tokens / 1_000_000) * self.INPUT_PRICE_PER_1M
        output_cost = (completion_tokens / 1_000_000) * self.OUTPUT_PRICE_PER_1M
        return input_cost + output_cost

    async def run_single_test(self, test_case: Dict) -> Dict:
        start_time = time.perf_counter()

        question = test_case.get("question", "")
        expected_answer = test_case.get("expected_answer", "")

        try:
            response = await self.agent.query(question)
        except Exception as exc:
            latency = time.perf_counter() - start_time
            return {
                "case_id": test_case.get("id", "unknown"),
                "test_case": question,
                "agent_response": "",
                "retrieved_ids": [],
                "contexts": [],
                "latency": latency,
                "ragas": {
                    "faithfulness": 0.0,
                    "relevancy": 0.0,
                    "retrieval": {"hit_rate": 0.0, "mrr": 0.0},
                },
                "judge": {
                    "final_score": 1.0,
                    "agreement_rate": 0.0,
                    "reasoning": f"Agent error: {exc}",
                    "conflict_resolved": False,
                    "individual_scores": {},
                },
                "status": "fail",
                "error": str(exc),
            }

        metadata = response.get("metadata", {})
        prompt_tokens = int(metadata.get("prompt_tokens", 0) or 0)
        completion_tokens = int(metadata.get("completion_tokens", 0) or 0)
        tokens_used = int(metadata.get("tokens_used", 0) or 0)

        if prompt_tokens == 0 and completion_tokens == 0 and tokens_used > 0:
            prompt_tokens = int(tokens_used * 0.7)
            completion_tokens = tokens_used - prompt_tokens

        request_cost = self._estimate_cost(prompt_tokens, completion_tokens)
        self.cost_tracker["total_tokens"] += tokens_used or (prompt_tokens + completion_tokens)
        self.cost_tracker["total_cost_usd"] += request_cost

        ragas_task = self.evaluator.score(test_case, response)
        judge_task = self.judge.evaluate_multi_judge(
            question,
            response.get("answer", ""),
            expected_answer,
        )
        ragas_result, judge_result = await asyncio.gather(
            ragas_task,
            judge_task,
            return_exceptions=True,
        )

        if isinstance(ragas_result, Exception):
            ragas_scores = {
                "faithfulness": 0.0,
                "relevancy": 0.0,
                "retrieval": {"hit_rate": 0.0, "mrr": 0.0},
                "error": str(ragas_result),
            }
        else:
            ragas_scores = ragas_result

        if isinstance(judge_result, Exception):
            judge_scores = {
                "final_score": 1.0,
                "agreement_rate": 0.0,
                "reasoning": f"Judge error: {judge_result}",
                "conflict_resolved": False,
                "individual_scores": {},
            }
        else:
            judge_scores = judge_result

        latency = time.perf_counter() - start_time
        final_score = float(judge_scores.get("final_score", 0.0) or 0.0)

        return {
            "case_id": test_case.get("id", "unknown"),
            "test_case": question,
            "expected_answer": expected_answer,
            "agent_response": response.get("answer", ""),
            "retrieved_ids": response.get("retrieved_ids", []),
            "contexts": response.get("contexts", []),
            "latency": latency,
            "ragas": ragas_scores,
            "judge": judge_scores,
            "token_usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": tokens_used or (prompt_tokens + completion_tokens),
                "estimated_cost_usd": round(request_cost, 8),
            },
            "status": "fail" if final_score < 3.0 else "pass",
        }

    async def run_all(self, dataset: List[Dict], batch_size: int = 5) -> List[Dict]:
        """Run benchmark in async batches and show progress."""
        results = []

        with tqdm(total=len(dataset), desc="Benchmark", unit="case") as progress:
            for i in range(0, len(dataset), batch_size):
                batch = dataset[i : i + batch_size]
                tasks = [self.run_single_test(case) for case in batch]
                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)
                progress.update(len(batch_results))

        print(f"Tong chi phi uoc tinh: ${self.cost_tracker['total_cost_usd']:.4f}")
        print(f"Tong tokens: {self.cost_tracker['total_tokens']:,}")
        return results
