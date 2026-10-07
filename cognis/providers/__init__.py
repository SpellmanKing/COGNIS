"""Módulo de provedores de inferência LLM da arquitetura COGNIS."""
from cognis.providers.base import LLMProvider, LLMResponse
from cognis.providers.mock import MockLLMProvider
from cognis.providers.adapter import CallableLLMAdapter
from cognis.providers.openai_provider import OpenAILLMProvider
from cognis.providers.ollama_provider import OllamaLLMProvider

__all__ = [
    "LLMProvider",
    "LLMResponse",
    "MockLLMProvider",
    "CallableLLMAdapter",
    "OpenAILLMProvider",
    "OllamaLLMProvider"
]
