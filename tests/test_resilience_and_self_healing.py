"""Testes unitários para mecanismos de resiliência, retry e self-healing."""
from cognis.resilience.retry import SelfHealingManager, RetryConfig
from cognis.resilience.fallback import FallbackPolicy
from cognis.providers.mock import MockLLMProvider
from cognis.domain.enums import ActionType


def test_clean_json_markdown_blocks():
    raw_markdown = "```json\n{\"acao\": \"AVANCAR\", \"justificativa\": \"Avançar agora mesmo.\", \"urgencia\": \"ALTA\"}\n```"
    cleaned = SelfHealingManager.clean_json_markdown(raw_markdown)
    assert not cleaned.startswith("```")
    assert not cleaned.endswith("```")
    assert '"acao": "AVANCAR"' in cleaned


def test_self_healing_recovers_from_syntax_failure():
    # Configura o mock para falhar na primeira vez e recuperar no retry
    mock_provider = MockLLMProvider(
        fail_profiles={"oportunista": "syntax"},
        heal_on_retry=True
    )

    manager = SelfHealingManager(RetryConfig(max_retries=1, enable_self_healing=True))
    prompt = "Perfil: Oportunista. O que você fará?"

    result = manager.process_with_recovery(mock_provider, prompt)

    assert result.is_valid is True
    assert result.recovered_by_retry is True
    assert result.attempts == 2
    assert result.decision.acao == ActionType.COLETAR_RECURSO
    assert result.failure_reason is None


def test_self_healing_falls_back_when_unrecoverable():
    # Configura o mock para falhar e NÃO se recuperar no retry
    mock_provider = MockLLMProvider(
        fail_profiles={"oportunista": "syntax"},
        heal_on_retry=False
    )

    manager = SelfHealingManager(RetryConfig(max_retries=1, enable_self_healing=True))
    prompt = "Perfil: Oportunista. O que você fará?"

    result = manager.process_with_recovery(mock_provider, prompt)

    assert result.is_valid is False
    assert result.recovered_by_retry is False
    assert result.decision.acao == ActionType.INATIVO
    assert result.failure_reason is not None
    assert "Erro de sintaxe JSON" in result.failure_reason


def test_fallback_policy_creates_inactive_action():
    decisao = FallbackPolicy.create_inactive_decision()
    assert decisao.acao == ActionType.INATIVO
    assert decisao.urgencia == "BAIXA"
    assert "inativo devido a erro de validação" in decisao.justificativa
