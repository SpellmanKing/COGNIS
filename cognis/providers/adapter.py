"""Adaptador para funções e callbacks de inferência legados."""
from typing import Callable, Union
from cognis.providers.base import LLMProvider, LLMResponse


class CallableLLMAdapter(LLMProvider):
    """Adapta qualquer função ou callable `(prompt: str) -> str` para a interface LLMProvider.

    Garante 100% de compatibilidade retroativa com códigos que utilizavam o
    parâmetro `conector_llm_callback`.
    """

    def __init__(self, callback: Callable[[str], Union[str, LLMResponse]], model_name: str = "custom_callback"):
        self._callback = callback
        self._model_name = model_name

    def generate(self, prompt: str) -> LLMResponse:
        result = self._callback(prompt)
        if isinstance(result, LLMResponse):
            return result
        return LLMResponse(content=str(result), model_name=self._model_name)
