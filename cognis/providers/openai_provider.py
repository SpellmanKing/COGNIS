"""Conector para inferência via OpenAI API (ou endpoints compatíveis como vLLM/Groq/OpenRouter)."""
import os
from typing import Optional, Dict, Any
from cognis.providers.base import LLMProvider, LLMResponse
from cognis.domain.exceptions import ProviderInferenceError


class OpenAILLMProvider(LLMProvider):
    """Provedor para OpenAI API e endpoints compatíveis com /v1/chat/completions."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        temperature: float = 0.1,
        timeout: float = 30.0
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.timeout = timeout

    def generate(self, prompt: str) -> LLMResponse:
        import httpx

        if not self.api_key:
            raise ProviderInferenceError(
                "Chave de API OpenAI não encontrada. Configure a variável OPENAI_API_KEY ou informe api_key no construtor."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "Você é o núcleo decisório de um agente autônomo. Responda APENAS com JSON estrito."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "response_format": {"type": "json_object"}
        }

        url = f"{self.base_url}/chat/completions"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return LLMResponse(
                content=content,
                model_name=self.model_name,
                tokens_prompt=usage.get("prompt_tokens"),
                tokens_completion=usage.get("completion_tokens"),
                metadata=data
            )
        except Exception as e:
            raise ProviderInferenceError(f"Falha na inferência via OpenAI API: {str(e)}") from e
