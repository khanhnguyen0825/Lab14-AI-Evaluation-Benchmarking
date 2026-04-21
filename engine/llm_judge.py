import asyncio
import os
import json
import statistics
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import AsyncOpenAI
import anthropic

load_dotenv()

class LLMJudge:
    def __init__(self, models: list = None):
        if models is None:
            models = ["gpt-4o", "claude-haiku-4-5"]
        # Use None as default to let the library handle missing keys properly
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.models = models
        
        self.rubrics = {
            "accuracy": "Chấm 1-5: 5=Đúng hoàn toàn, 4=Đúng chính, 3=Một phần, 2=Phần lớn sai, 1=Hoàn toàn sai",
            "completeness": "Chấm 1-5: Câu trả lời có đủ thông tin cần thiết không?",
            "tone": "Chấm 1-5: Ngôn ngữ có chuyên nghiệp, phù hợp không?",
            "hallucination": "Chấm 1-5: 5=Không bịa, 1=Bịa hoàn toàn"
        }

    def _build_prompt(self, question: str, answer: str, ground_truth: str) -> str:
        return f"""Bạn là một giám khảo chuyên gia đánh giá chất lượng câu trả lời của AI.
Hãy đánh giá câu trả lời dựa trên câu hỏi và đáp án chuẩn (ground truth).

Câu hỏi: {question}
Đáp án chuẩn: {ground_truth}
Câu trả lời của AI: {answer}

Tiêu chí đánh giá:
- Độ chính xác (accuracy): {self.rubrics['accuracy']}
- Tính đầy đủ (completeness): {self.rubrics['completeness']}
- Giọng điệu (tone): {self.rubrics['tone']}
- Tính chân thực (hallucination): {self.rubrics['hallucination']}

Hãy trả về CHỈ MỘT chuỗi JSON với cấu trúc sau, không có markdown formatting hay text dư thừa:
{{"score": <điểm số tổng hợp từ 1-5, nguyên>, "reasoning": "<lời giải thích ngắn gọn>"}}
"""

    async def _call_openai(self, prompt: str, model="gpt-4o") -> Dict:
        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"score": 3, "reasoning": f"Error calling OpenAI {model}: {str(e)}"}

    async def _call_anthropic(self, prompt: str, model="claude-haiku-4-5") -> Dict:
        try:
            response = await self.anthropic_client.messages.create(
                model=model,
                max_tokens=500,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt + "\n\nTrả về chỉ chuỗi JSON:"}]
            )
            text = response.content[0].text.strip()
            if text.startswith("```json"):
                text = text.split("```json")[1].split("```")[0].strip()
            elif text.startswith("```"):
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception as e:
            return {"score": 3, "reasoning": f"Error calling Anthropic {model}: {str(e)}"}

    async def evaluate_multi_judge(self, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        prompt = self._build_prompt(question, answer, ground_truth)
        
        tasks = []
        model_names = []
        if "gpt-4o" in self.models:
            tasks.append(self._call_openai(prompt, model="gpt-4o"))
            model_names.append("gpt-4o")
        if "gpt-4o-mini" in self.models:
            tasks.append(self._call_openai(prompt, model="gpt-4o-mini"))
            model_names.append("gpt-4o-mini")
        if "claude-haiku-4-5" in self.models:
            tasks.append(self._call_anthropic(prompt, model="claude-haiku-4-5"))
            model_names.append("claude-haiku-4-5")
            
        results = await asyncio.gather(*tasks)
        
        score_a = int(results[0].get("score", 3)) if len(results) > 0 else 3
        score_b = int(results[1].get("score", 3)) if len(results) > 1 else score_a
        
        diff = abs(score_a - score_b)
        conflict_resolved = False
        final_score = 0.0
        score_tiebreak = 0
        
        if diff <= 1:
            final_score = (score_a + score_b) / 2.0
            agreement_rate = 1.0 if diff == 0 else 0.5
        else:
            conflict_resolved = True
            agreement_rate = 0.0
            tiebreaker_result = await self._call_openai(prompt, model="gpt-4o-mini")
            score_tiebreak = int(tiebreaker_result.get("score", 3))
            final_score = float(statistics.median([score_a, score_b, score_tiebreak]))
            results.append(tiebreaker_result)
        
        individual_scores = {}
        for idx, m_name in enumerate(model_names):
            individual_scores[m_name] = results[idx]
        
        reasoning = f"A={score_a}, B={score_b}"
        if conflict_resolved:
            reasoning += f", Tiebreaker={score_tiebreak}"
            
        return {
            "final_score": final_score,
            "agreement_rate": agreement_rate,
            "individual_scores": individual_scores,
            "conflict_resolved": conflict_resolved,
            "reasoning": reasoning
        }

    async def check_position_bias(self, response_a: str, response_b: str) -> Dict:
        """
        Nâng cao: Thực hiện đổi chỗ response A và B để xem Judge có thiên vị vị trí không.
        """
        prompt_ab = f"So sánh 2 câu trả lời: A='{response_a}', B='{response_b}'. Trả về JSON: {{\"preferred\": \"A\" hoặc \"B\"}}"
        prompt_ba = f"So sánh 2 câu trả lời: A='{response_b}', B='{response_a}'. Trả về JSON: {{\"preferred\": \"A\" hoặc \"B\"}}"
        
        task1 = self._call_openai(prompt_ab, model="gpt-4o-mini")
        task2 = self._call_openai(prompt_ba, model="gpt-4o-mini")
        res1, res2 = await asyncio.gather(task1, task2)
        
        pref1 = res1.get("preferred", "A")
        pref2 = res2.get("preferred", "A")
        
        bias_detected = False
        if pref1 == "A" and pref2 == "A":
            bias_detected = True
            
        return {
            "bias_detected": bias_detected,
            "score_order_AB": pref1,
            "score_order_BA": pref2
        }

if __name__ == "__main__":
    import sys
    
    # Fix Windows console encoding for Vietnamese characters
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    async def main():
        judge = LLMJudge()
        question = "Làm thế nào đặt lại mật khẩu?"
        answer = "Vào Settings rồi bấm Reset Password."
        ground_truth = "Vào Cài đặt → Bảo mật → Đổi mật khẩu."
        
        print("[TEST] Bat dau evaluate_multi_judge...")
        res = await judge.evaluate_multi_judge(question, answer, ground_truth)
        print("\n[RESULT] Ket qua cham diem:")
        print(json.dumps(res, indent=2, ensure_ascii=False))
        
    asyncio.run(main())
