"""Testes unitários para provedores de inferência e adaptadores."""
import pytest
from cognis.providers.base import LLMResponse
from cognis.providers.adapter import CallableLLMAdapter
from cognis.providers.mock import MockLLMProvider
from cognis.providers.openai_provider import OpenAILLMProvider
from cognis.domain.exceptions import ProviderInferenceError


def test_callable_llm_adapter():
    def dummy_func(prompt: str) -> str:
        return f"Echo: {prompt}"

    adapter = CallableLLMAdapter(dummy_func)
    resp = adapter.generate("Olá mundo")

    assert isinstance(resp, LLMResponse)
    assert resp.content == "Echo: Olá mundo"
    assert resp.model_name == "custom_callback"


def test_mock_provider_error_modes():
    provider = MockLLMProvider(
        fail_profiles={"agressivo": "semantic", "defensivo": "markdown_broken"}
    )

    resp_semantico = provider.generate("Perfil: Agressivo. Decida.")
    assert "DORMIR_NO_PONTO" in resp_semantico.content

    resp_md = provider.generate("Perfil: Defensivo. Decida.")
    assert "```json" in resp_md.content


def test_openai_provider_missing_key_raises_domain_error():
    provider = OpenAILLMProvider(api_key="")
    with pytest.raises(ProviderInferenceError) as exc:
        provider.generate("Qualquer prompt")
    assert "Chave de API OpenAI não encontrada" in str(exc.value)
