"""Testes unitários para o DecisionEngine e execução multiagente."""
from cognis.core.engine import DecisionEngine
from cognis.providers.mock import MockLLMProvider
from cognis.repository.json_repository import JsonDecisionRepository
from cognis.domain.enums import ActionType


def test_decision_engine_run_multi_profile(tmp_path):
    output_file = tmp_path / "test_doc_5.json"
    repo = JsonDecisionRepository(file_path=output_file, legacy_mode=True)

    # 3 perfis funcionam perfeitamente, 1 falha sem autocorreção para testar fallback INATIVO
    mock_provider = MockLLMProvider(
        fail_profiles={"oportunista": "syntax"},
        heal_on_retry=False
    )

    engine = DecisionEngine(
        llm_provider=mock_provider,
        repository=repo
    )

    percepcao = {
        "ciclo": 1,
        "posicao_atual": {"x": 12, "y": 8},
        "energia_restante": 78,
        "ameacas_detectadas": [{"tipo": "Inimigo", "distancia": 3}],
        "recursos_no_raio": [{"tipo": "Bateria", "distancia": 1}]
    }

    records = engine.run_multi_profile_cycle(cycle_id=1, perception_state=percepcao)

    assert len(records) == 4

    # Mapeia decisões por perfil
    decisoes_por_perfil = {r.perfil_estrategico: r for r in records}

    assert decisoes_por_perfil["Agressivo"].decisao_executada.acao == ActionType.AVANCAR
    assert decisoes_por_perfil["Agressivo"].resposta_valida is True

    assert decisoes_por_perfil["Defensivo"].decisao_executada.acao == ActionType.DEFENDER
    assert decisoes_por_perfil["Defensivo"].resposta_valida is True

    assert decisoes_por_perfil["Explorador"].decisao_executada.acao == ActionType.PATRULHAR
    assert decisoes_por_perfil["Explorador"].resposta_valida is True

    # Oportunista deve ter acionado fallback para INATIVO
    assert decisoes_por_perfil["Oportunista"].decisao_executada.acao == ActionType.INATIVO
    assert decisoes_por_perfil["Oportunista"].resposta_valida is False
    assert decisoes_por_perfil["Oportunista"].motivo_inativo is not None

    # Verifica persistência no arquivo temporário
    assert output_file.exists()


def test_decision_engine_with_successful_self_healing(tmp_path):
    output_file = tmp_path / "test_doc_5_healed.json"
    repo = JsonDecisionRepository(file_path=output_file, legacy_mode=True)

    # Oportunista falha no primeiro envio mas se cura no retry
    mock_provider = MockLLMProvider(
        fail_profiles={"oportunista": "syntax"},
        heal_on_retry=True
    )

    engine = DecisionEngine(
        llm_provider=mock_provider,
        repository=repo
    )

    percepcao = {"ciclo": 1}
    records = engine.run_multi_profile_cycle(cycle_id=1, perception_state=percepcao)

    decisoes = {r.perfil_estrategico: r for r in records}
    oportunista = decisoes["Oportunista"]

    assert oportunista.resposta_valida is True
    assert oportunista.recuperado_por_retry is True
    assert oportunista.tentativas_executadas == 2
    assert oportunista.decisao_executada.acao == ActionType.COLETAR_RECURSO
