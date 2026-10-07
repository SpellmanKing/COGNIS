"""Registro centralizado e Factory de estratégias táticas (Pattern Registry / Factory)."""
from typing import Dict, List, Optional
from cognis.strategies.base import TacticalStrategy
from cognis.strategies.concrete import (
    AggressiveStrategy,
    DefensiveStrategy,
    ExplorerStrategy,
    OpportunisticStrategy,
    DynamicTacticalStrategy
)
from cognis.domain.exceptions import StrategyNotFoundError


class StrategyRegistry:
    """Repositório em memória e catálogo de estratégias táticas ativas."""

    def __init__(self):
        self._strategies: Dict[str, TacticalStrategy] = {}

    def register(self, strategy: TacticalStrategy) -> "StrategyRegistry":
        """Registra uma estratégia pelo nome."""
        self._strategies[strategy.name.lower()] = strategy
        return self

    def get(self, name: str) -> TacticalStrategy:
        """Obtém uma estratégia pelo nome (case-insensitive)."""
        clean_name = name.strip().lower()
        if clean_name not in self._strategies:
            raise StrategyNotFoundError(
                f"Estratégia '{name}' não encontrada. Estratégias disponíveis: {list(self._strategies.keys())}"
            )
        return self._strategies[clean_name]

    def has(self, name: str) -> bool:
        return name.strip().lower() in self._strategies

    def list_all(self) -> List[TacticalStrategy]:
        """Retorna todas as estratégias registradas na ordem de inserção."""
        return list(self._strategies.values())

    def list_names(self) -> List[str]:
        return [s.name for s in self._strategies.values()]

    @classmethod
    def create_canonical_registry(cls) -> "StrategyRegistry":
        """Cria um registro pré-populado com os 4 perfis canônicos do Subgrupo C."""
        registry = cls()
        registry.register(AggressiveStrategy())
        registry.register(DefensiveStrategy())
        registry.register(ExplorerStrategy())
        registry.register(OpportunisticStrategy())
        return registry

    @classmethod
    def from_dict(cls, perfis: Dict[str, str]) -> "StrategyRegistry":
        """Cria o registro a partir de um dicionário {'Nome': 'Diretriz'}, garantindo retrocompatibilidade."""
        registry = cls()
        canonical_map = {
            "agressivo": AggressiveStrategy,
            "defensivo": DefensiveStrategy,
            "explorador": ExplorerStrategy,
            "oportunista": OpportunisticStrategy,
        }
        for nome, diretriz in perfis.items():
            key = nome.strip().lower()
            if key in canonical_map:
                strategy = canonical_map[key](directive=diretriz)
            else:
                strategy = DynamicTacticalStrategy(name=nome, directive=diretriz)
            registry.register(strategy)
        return registry
