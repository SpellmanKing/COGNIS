"""Conector para inferência via servidor local Ollama."""
from typing import Optional, Dict, Any
from cognis.providers.base import LLMProvider, LLMResponse
from cognis.domain.exceptions import ProviderInferenceError


class OllamaLLMProvider(LLMProvider):
    """Provedor para modelos locais executados no Ollama (ex: llama3, mistral, qwen2.5)."""

    def __init__(
        self,
        model_name: str = "llama3:8b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.1,
        timeout: float = 60.0
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.timeout = timeout

    def generate(self, prompt: str) -> LLMResponse:
        import httpx

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": self.temperature
            }
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

            content = data.get("response", "")
            return LLMResponse(
                content=content,
                model_name=self.model_name,
                tokens_prompt=data.get("prompt_eval_count"),
                tokens_completion=data.get("eval_count"),
                metadata=data
            )
        except Exception as e:
            raise ProviderInferenceError(f"Falha na comunicação com o servidor Ollama em {self.base_url}: {str(e)}") from e
