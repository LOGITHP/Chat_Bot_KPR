import os
import re
from typing import Dict, Any, List
from openai import OpenAI
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

        api_key = config.OPENAI_API_KEY or "ollama"
        base_url = config.OPENAI_BASE_URL or "http://localhost:11434/v1"
        self.model_name = config.LLM_MODEL_NAME

        print(f"[RAGEngine] Initializing OpenAI client (Base URL: '{base_url}', Model: '{self.model_name}')")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.chat_history: List[Dict[str, str]] = []

    def clear_history(self):
        """Clears the active conversation history."""
        self.chat_history.clear()
        print("[RAGEngine] Conversation history cleared.")

    def generate_response(self, question: str, top_k: int = config.TOP_K, use_history: bool = True, max_history_turns: int = 5) -> Dict[str, Any]:
        """Retrieves context from Qdrant and generates an answer using OpenAI-compatible LLM with chat history memory."""
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
            "Use the provided context documents and conversation history to answer the user's question clearly and concisely. "
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

        # 3. Construct messages payload with chat history memory
        messages = [{"role": "system", "content": system_prompt}]

        if use_history and self.chat_history:
            # Include recent chat history turns
            recent_history = self.chat_history[-(max_history_turns * 2):]
            messages.extend(recent_history)

        messages.append({"role": "user", "content": user_prompt})

        # 4. Call LLM API (Ollama / OpenAI / Groq via OpenAI client)
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=0.2,
                max_tokens=1024
            )
            raw_text = chat_completion.choices[0].message.content or ""
            answer = extract_clean_answer(raw_text)

            # Store turn in conversation history if generation succeeded
            if use_history and answer and not answer.startswith("Error generating response"):
                self.chat_history.append({"role": "user", "content": question})
                self.chat_history.append({"role": "assistant", "content": answer})

        except Exception as e:
            answer = f"Error generating response from LLM ({self.model_name}): {str(e)}"

        return {
            "question": question,
            "answer": answer,
            "sources": context_matches
        }



if __name__ == "__main__":
    engine = RAGEngine()
    response = engine.generate_response("What is IGNITRRON?")
    print("Answer:\n", response["answer"])
