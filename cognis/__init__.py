"""COGNIS - Arquitetura de Motor de Decisão de Agentes Autônomos (Subgrupo C)."""
from cognis.domain.models import (
    Coordenada,
    StrategicScratchpad,
    DecisaoAgente,
    CycleDecisionRecord
)
from cognis.domain.enums import ActionType, UrgencyLevel, RiskLevel
from cognis.strategies.base import TacticalStrategy
from cognis.strategies.registry import StrategyRegistry
from cognis.strategies.concrete import (
    AggressiveStrategy,
    DefensiveStrategy,
    ExplorerStrategy,
    OpportunisticStrategy
)
from cognis.providers.base import LLMProvider, LLMResponse
from cognis.providers.mock import MockLLMProvider
from cognis.providers.adapter import CallableLLMAdapter
from cognis.resilience.retry import SelfHealingManager, RetryConfig
from cognis.resilience.fallback import FallbackPolicy
from cognis.repository.base import DecisionRepository, UnitOfWork
from cognis.repository.json_repository import JsonDecisionRepository
from cognis.core.prompt_builder import DynamicPromptBuilder
from cognis.core.engine import DecisionEngine
from cognis.compatibility import AgenteCicloIA

__version__ = "2.0.0"

__all__ = [
    "Coordenada",
    "StrategicScratchpad",
    "DecisaoAgente",
    "CycleDecisionRecord",
    "ActionType",
    "UrgencyLevel",
    "RiskLevel",
    "TacticalStrategy",
    "StrategyRegistry",
    "AggressiveStrategy",
    "DefensiveStrategy",
    "ExplorerStrategy",
    "OpportunisticStrategy",
    "LLMProvider",
    "LLMResponse",
    "MockLLMProvider",
    "CallableLLMAdapter",
    "SelfHealingManager",
    "RetryConfig",
    "FallbackPolicy",
    "DecisionRepository",
    "UnitOfWork",
    "JsonDecisionRepository",
    "DynamicPromptBuilder",
    "DecisionEngine",
    "AgenteCicloIA"
]
