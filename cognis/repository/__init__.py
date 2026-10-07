"""Módulo de repositórios e persistência da arquitetura COGNIS."""
from cognis.repository.base import DecisionRepository, UnitOfWork
from cognis.repository.json_repository import JsonDecisionRepository

__all__ = [
    "DecisionRepository",
    "UnitOfWork",
    "JsonDecisionRepository"
]
