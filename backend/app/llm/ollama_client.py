from openai import AsyncOpenAI
from app.config import settings
from typing import List, Dict, Any

class OllamaClient:
    def __init__(self):
        base_url = settings.effective_llm_base_url
        model = settings.effective_model_name
        api_key = settings.effective_api_key
        print(f"[OllamaClient] Initializing with base URL: {base_url}, model: {model}")
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model

    async def generate_chat_completion(self, messages: List[Dict[str, str]], max_tokens: int = 1024, temperature: float = 0.2) -> str:
        try:
            response = await self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"[OllamaClient Error] Failed to generate response: {e}")
            return "I apologize, but I am unable to connect to the LLM service at this moment."

ollama_client = OllamaClient()
