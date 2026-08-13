from openai import AsyncOpenAI
from app.config import settings
from typing import List, Dict, Any

class OllamaClient:
    def __init__(self):
        print(f"[OllamaClient] Initializing with base URL: {settings.OLLAMA_URL} and model: {settings.OLLAMA_MODEL}")
        # Use v1 endpoint for OpenAI compatibility
        base_url = f"{settings.OLLAMA_URL}/v1"
        self.client = AsyncOpenAI(api_key="ollama", base_url=base_url)
        self.model_name = settings.OLLAMA_MODEL

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
