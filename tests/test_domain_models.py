"""Testes unitários para modelos de domínio e validação Pydantic v2."""
import pytest
from pydantic import ValidationError
from cognis.domain.models import DecisaoAgente, Coordenada, StrategicScratchpad
from cognis.domain.enums import ActionType, UrgencyLevel, RiskLevel


def test_decisao_agente_valida_simples():
    dados = {
        "acao": "DEFENDER",
        "justificativa": "Posição sob risco moderado; mantendo postura defensiva.",
        "urgencia": "MEDIA"
    }
    decisao = DecisaoAgente.model_validate(dados)
    assert decisao.acao == ActionType.DEFENDER
    assert decisao.alvo_coordenada is None
    assert decisao.urgencia == UrgencyLevel.MEDIA


def test_decisao_agente_com_coordenadas_e_scratchpad():
    dados = {
        "scratchpad": {
            "analise_situacional": "Ameaça a 3 células de distância, energia suficiente.",
            "ponderacao_risco": "ALTO",
            "hipotese_tatica": "Avançar imediatamente para neutralizar oponente."
        },
        "acao": "AVANCAR",
        "justificativa": "Avanço tático prioritário para engajamento.",
        "alvo_coordenada": {"x": 15, "y": 8},
        "urgencia": "ALTA"
    }
    decisao = DecisaoAgente.model_validate(dados)
    assert decisao.acao == ActionType.AVANCAR
    assert decisao.alvo_coordenada.x == 15
    assert decisao.alvo_coordenada.y == 8
    assert decisao.scratchpad.ponderacao_risco == RiskLevel.ALTO


def test_decisao_rejeita_acao_invalida():
    dados = {
        "acao": "DORMIR",
        "justificativa": "Agente resolveu descansar no mapa.",
        "urgencia": "BAIXA"
    }
    with pytest.raises(ValidationError) as exc:
        DecisaoAgente.model_validate(dados)
    assert "acao" in str(exc.value)


def test_decisao_rejeita_justificativa_curta():
    dados = {
        "acao": "DEFENDER",
        "justificativa": "curto",
        "urgencia": "MEDIA"
    }
    with pytest.raises(ValidationError) as exc:
        DecisaoAgente.model_validate(dados)
    assert "justificativa" in str(exc.value)


def test_decisao_rejeita_justificativa_apenas_espacos():
    dados = {
        "acao": "DEFENDER",
        "justificativa": "          ",
        "urgencia": "MEDIA"
    }
    with pytest.raises(ValidationError):
        DecisaoAgente.model_validate(dados)


def test_decisao_to_documento_5_dict():
    decisao = DecisaoAgente(
        acao=ActionType.PATRULHAR,
        justificativa="Mapeando quadrantes adjacentes de baixa visibilidade.",
        alvo_coordenada=Coordenada(x=10, y=10),
        urgencia=UrgencyLevel.BAIXA
    )
    doc_dict = decisao.to_documento_5_dict()
    assert doc_dict["acao"] == "PATRULHAR"
    assert doc_dict["alvo_coordenada"] == {"x": 10, "y": 10}
    assert doc_dict["urgencia"] == "BAIXA"
