import asyncio
import os
import re
import math
from typing import Dict, List, Tuple

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()


class MainAgent:
    """Simple async RAG agent with keyword retrieval and OpenAI generation."""

    def __init__(
        self,
        system_prompt: str | None = None,
        model: str = "gpt-4o-mini",
        name: str = "SupportAgent-v1",
        documents: List[Dict] | None = None,
        max_context_chars: int = 320,
        max_output_tokens: int = 180,
    ):
        self.name = name
        self.model = model
        self.max_context_chars = max_context_chars
        self.max_output_tokens = max_output_tokens
        self.system_prompt = system_prompt or (
            "Ban la tro ly ho tro khach hang. Chi su dung context duoc cung cap. "
            "Neu context khong du, hay noi ro khong du thong tin va khong du doan them."
        )

        api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None

        self.documents = documents or []

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        # Unicode-aware tokenizer to preserve Vietnamese words with diacritics.
        return re.findall(r"\b\w+\b", text.lower(), flags=re.UNICODE)

    def _retrieve_top_k(self, question: str, k: int = 3) -> List[Dict]:
        if not self.documents:
            return []

        q_tokens = set(self._tokenize(question))
        scored_docs: List[Tuple[float, Dict]] = []

        for doc in self.documents:
            d_tokens = set(self._tokenize(doc["content"]))
            overlap = len(q_tokens.intersection(d_tokens))
            if not d_tokens:
                score = 0.0
            else:
                score = overlap / math.sqrt(len(d_tokens))
            scored_docs.append((score, doc))

        scored_docs.sort(key=lambda item: item[0], reverse=True)
        top_docs = [doc for _, doc in scored_docs[:k]]

        if not top_docs:
            top_docs = self.documents[:k]
        return top_docs

    @staticmethod
    def _fallback_answer(question: str, contexts: List[str], concise_mode: bool) -> str:
        if not contexts:
            return "Khong tim thay context phu hop de tra loi cau hoi nay."

        if concise_mode:
            return (
                "Thong tin tim thay: "
                f"{contexts[0]}"
            )

        return (
            "Tra loi dua tren context:\n"
            f"- Cau hoi: {question}\n"
            f"- Trich dan 1: {contexts[0]}\n"
            + (f"- Trich dan 2: {contexts[1]}\n" if len(contexts) > 1 else "")
            + "Neu can them thong tin, vui long kiem tra tai lieu goc."
        )

    async def query(self, question: str) -> Dict:
        top_docs = self._retrieve_top_k(question, k=3)
        retrieved_ids = [doc["id"] for doc in top_docs]
        contexts = [doc["content"][: self.max_context_chars] for doc in top_docs]
        concise_mode = "tra loi ngan gon" in self.system_prompt.lower()
        context_block = "\n\n".join(
            [f"[{doc['id']}] {doc['content'][: self.max_context_chars]}" for doc in top_docs]
        )

        prompt = (
            "Context:\n"
            f"{context_block}\n\n"
            "Question:\n"
            f"{question}\n\n"
            "Answer in Vietnamese and cite document IDs used."
        )

        answer = self._fallback_answer(question, contexts, concise_mode)
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        error = None

        if self.client is not None:
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                    max_tokens=self.max_output_tokens,
                )
                answer = response.choices[0].message.content or answer
                usage = response.usage
                if usage:
                    prompt_tokens = usage.prompt_tokens or 0
                    completion_tokens = usage.completion_tokens or 0
                    total_tokens = usage.total_tokens or (prompt_tokens + completion_tokens)
            except Exception as exc:
                error = str(exc)

        if total_tokens == 0:
            total_tokens = max(1, len(prompt) // 4)
            prompt_tokens = int(total_tokens * 0.7)
            completion_tokens = total_tokens - prompt_tokens

        return {
            "answer": answer,
            "contexts": contexts,
            "retrieved_ids": retrieved_ids,
            "metadata": {
                "model": self.model,
                "tokens_used": total_tokens,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "sources": [doc["source"] for doc in top_docs],
                "agent_name": self.name,
                "error": error,
            },
        }


if __name__ == "__main__":
    async def _test() -> None:
        agent = MainAgent()
        resp = await agent.query("Lam the nao de doi mat khau?")
        print(resp)

    asyncio.run(_test())
