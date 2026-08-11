import os
import re
from typing import Dict, Any, List, Optional
from openai import OpenAI
import config
from services.vector_store import vector_store

def extract_clean_answer(text: str) -> str:
    """Strips thinking blocks, <think> tags, and reasoning scratchpads from model outputs."""
    if not text:
        return ""
    if "</think>" in text:
        text = text.split("</think>")[-1].strip()
    if "<think>" in text:
        text = text.split("<think>")[-1].strip()

    if "Here's a thinking process:" in text or "1.  **Analyze" in text:
        for marker in ["\n\nBased on ", "\nBased on ", "\n\nHere are ", "\nHere are ", "\n\nAnswer:", "\nAnswer:"]:
            if marker in text:
                return text.split(marker)[-1].strip()
        lines = text.split("\n")
        filtered = []
        for line in lines:
            sline = line.strip()
            if sline.startswith("Here's a thinking process") or sline.startswith(("- Document", "1.  **", "2.  **", "3.  **", "4.  **", "5.  **")):
                continue
            filtered.append(line)
        return "\n".join(filtered).strip()

    return text.strip()

class RAGEngine:
    """Retrieval-Augmented Generation engine powered by local Ollama model and Qdrant vector retrieval.
    Incorporates active conversation history for student queries.
    """

    def __init__(self):
        self.vector_store = vector_store
        api_key = config.OPENAI_API_KEY or "ollama"
        base_url = config.OPENAI_BASE_URL or "http://localhost:11434/v1"
        self.model_name = config.LLM_MODEL_NAME

        print(f"[RAGEngine] Initializing OpenAI client wrapper (Base URL: '{base_url}', Model: '{self.model_name}')")
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate_response(
        self,
        question: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        top_k: int = config.TOP_K,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieves document context from Qdrant and generates an answer using local Ollama model with history."""

        # 1. Search vector store
        context_matches = self.vector_store.search(question, top_k=top_k, category=category)

        if not context_matches:
            context_str = "No relevant context found in uploaded documents."
        else:
            context_str_list = []
            for idx, match in enumerate(context_matches):
                source_info = f"[File: {match['filename']}]" if match.get("filename") else ""
                context_str_list.append(f"Document {idx + 1} {source_info}:\n{match['text']}")
            context_str = "\n\n".join(context_str_list)

        # 2. System Prompt
        system_prompt = (
            "You are a helpful, smart, and precise College AI Assistant. "
            "Use the provided document context and conversation history to answer the user's question accurately. "
            "Respond directly with the answer. Do NOT output internal reasoning or scratchpad code. "
            "If the context does not contain the necessary information, state clearly that "
            "you do not have that specific detail in the uploaded knowledge base."
        )

        user_prompt = (
            f"Document Context:\n"
            f"---------------------\n"
            f"{context_str}\n"
            f"---------------------\n"
            f"User Question: {question}\n\n"
            f"Answer:"
        )

        # 3. Construct message history payload
        messages = [{"role": "system", "content": system_prompt}]

        if chat_history:
            # Include recent chat history turns
            recent_turns = chat_history[-10:] # last 5 exchanges
            for msg in recent_turns:
                role = msg.get("role", "user")
                if role in ["user", "assistant"]:
                    messages.append({"role": role, "content": msg.get("content", "")})

        messages.append({"role": "user", "content": user_prompt})

        # 4. Invoke LLM API
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=0.2,
                max_tokens=1024
            )
            raw_text = chat_completion.choices[0].message.content or ""
            answer = extract_clean_answer(raw_text)

        except Exception as e:
            print(f"[RAGEngine Warning] Ollama LLM call failed ({e}). Returning fallback response.")
            # Local fallback response if Ollama service is offline during local test
            if context_matches:
                fallback_snippet = context_matches[0]['text'][:300]
                answer = f"(Local Model Fallback Response based on context)\nBased on stored document '{context_matches[0]['filename']}':\n{fallback_snippet}..."
            else:
                answer = "I searched the knowledge base, but I couldn't reach the local Ollama LLM service or find exact matching details. Please ensure Ollama is running."

        return {
            "question": question,
            "answer": answer,
            "sources": context_matches
        }

# Singleton instance
rag_engine = RAGEngine()
