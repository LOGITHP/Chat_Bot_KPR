import os
import re
from typing import Dict, Any, List
from groq import Groq
import config
from vector_store import VectorStore

def extract_clean_answer(text: str) -> str:
    """Strips thinking blocks, <think> tags, and reasoning scratchpads from model outputs."""
    if not text:
        return ""
    if "</think>" in text:
        text = text.split("</think>")[-1].strip()
    if "<think>" in text:
        text = text.split("<think>")[-1].strip()

    if "Here's a thinking process:" in text or "1.  **Analyze" in text:
        # Search for transition markers to actual answer
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
    def __init__(self, vector_store: VectorStore = None):
        if vector_store is None:
            self.vector_store = VectorStore()
        else:
            self.vector_store = vector_store

        api_key = config.GROQ_API_KEY
        if not api_key:
            print("[Warning] GROQ_API_KEY is not set in environment or .env file.")
        
        self.groq_client = Groq(api_key=api_key)
        self.model_name = config.GROQ_MODEL_NAME

    def generate_response(self, question: str, top_k: int = config.TOP_K) -> Dict[str, Any]:
        """Retrieves context from Qdrant and generates an answer using Groq Qwen model."""
        # 1. Search vector store
        context_matches = self.vector_store.search(question, top_k=top_k)

        if not context_matches:
            context_str = "No relevant context found in college documents."
        else:
            context_str_list = []
            for idx, match in enumerate(context_matches):
                source_info = f"[Source: {match['source']}]" if match.get("source") else ""
                context_str_list.append(f"Document {idx + 1} {source_info}:\n{match['text']}")
            context_str = "\n\n".join(context_str_list)

        # 2. System and User Prompt setup
        system_prompt = (
            "You are a helpful and accurate AI assistant for the college. "
            "Use the provided context documents to answer the user's question clearly and concisely. "
            "Respond directly with the final answer. Do NOT output scratchpad or thinking steps. "
            "If the context does not contain enough information to answer the question, state politely that "
            "you do not have that specific information in the current data store."
        )

        user_prompt = (
            f"Context Information:\n"
            f"---------------------\n"
            f"{context_str}\n"
            f"---------------------\n"
            f"User Question: {question}\n\n"
            f"Answer:"
        )

        # 3. Call Groq LLM API
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model_name,
                temperature=0.2,
                max_tokens=1024
            )
            raw_text = chat_completion.choices[0].message.content or ""
            answer = extract_clean_answer(raw_text)
        except Exception as e:
            answer = f"Error generating response from Groq API ({self.model_name}): {str(e)}"

        return {
            "question": question,
            "answer": answer,
            "sources": context_matches
        }

        return {
            "question": question,
            "answer": answer,
            "sources": context_matches
        }

if __name__ == "__main__":
    engine = RAGEngine()
    response = engine.generate_response("What is IGNITRRON?")
    print("Answer:\n", response["answer"])
