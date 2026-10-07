"""Testes unitários para o padrão Strategy e Registry de Perfis Táticos."""
import pytest
from cognis.strategies.concrete import (
    AggressiveStrategy,
    DefensiveStrategy,
    ExplorerStrategy,
    OpportunisticStrategy
)
from cognis.strategies.registry import StrategyRegistry
from cognis.domain.exceptions import StrategyNotFoundError
from cognis.domain.enums import RiskLevel, ActionType


def test_quatro_perfis_canonicos_possuem_doutrinas_distintas():
    agressivo = AggressiveStrategy()
    defensivo = DefensiveStrategy()
    explorador = ExplorerStrategy()
    oportunista = OpportunisticStrategy()

    assert agressivo.risk_tolerance == RiskLevel.ALTO
    assert ActionType.AVANCAR in agressivo.preferred_actions

    assert defensivo.risk_tolerance == RiskLevel.BAIXO
    assert ActionType.DEFENDER in defensivo.preferred_actions

    assert explorador.risk_tolerance == RiskLevel.MEDIO
    assert ActionType.PATRULHAR in explorador.preferred_actions

    assert oportunista.risk_tolerance == RiskLevel.MEDIO
    assert ActionType.COLETAR_RECURSO in oportunista.preferred_actions


def test_registry_lookup_and_case_insensitivity():
    registry = StrategyRegistry.create_canonical_registry()

    assert registry.has("Agressivo")
    assert registry.has("agressivo")
    assert registry.has("AGRESSIVO")

    strat = registry.get("dEfEnSiVo")
    assert strat.name == "Defensivo"


def test_registry_raises_on_unknown():
    registry = StrategyRegistry.create_canonical_registry()
    with pytest.raises(StrategyNotFoundError):
        registry.get("NinjaInvisivel")


def test_registry_from_dict_preserves_custom_and_canonical():
    perfis = {
        "Agressivo": "Minha diretriz customizada agressiva.",
        "Customizado": "Fazer coisas novas."
    }
    registry = StrategyRegistry.from_dict(perfis)
    assert registry.has("Agressivo")
    assert registry.get("Agressivo").directive == "Minha diretriz customizada agressiva."
    assert registry.has("Customizado")
