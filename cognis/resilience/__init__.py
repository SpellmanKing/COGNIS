"""Módulo de resiliência e tratamento de falhas da arquitetura COGNIS."""
from cognis.resilience.fallback import FallbackPolicy
from cognis.resilience.retry import RetryConfig, ProcessingResult, SelfHealingManager

__all__ = [
    "FallbackPolicy",
    "RetryConfig",
    "ProcessingResult",
    "SelfHealingManager"
]
