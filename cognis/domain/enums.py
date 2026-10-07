"""Enums e tipos de domínio para o motor de decisão de agentes autônomos.

Define ações atômicas permitidas, níveis de urgência, tolerância ao risco e status de ciclo.
"""
from enum import Enum
from typing import Literal

# Ações atômicas permitidas no simulador do Subgrupo C
AcoesValidasLiteral = Literal[
    "AVANCAR",
    "RECUAR",
    "COLETAR_RECURSO",
    "DEFENDER",
    "PATRULHAR",
    "INATIVO"
]

class ActionType(str, Enum):
    """Conjunto estrito de ações executáveis pelos agentes autônomos."""
    AVANCAR = "AVANCAR"
    RECUAR = "RECUAR"
    COLETAR_RECURSO = "COLETAR_RECURSO"
    DEFENDER = "DEFENDER"
    PATRULHAR = "PATRULHAR"
    INATIVO = "INATIVO"


class UrgencyLevel(str, Enum):
    """Níveis de urgência operacional da ação."""
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class RiskLevel(str, Enum):
    """Nível de risco situacional avaliado pelo agente."""
    BAIXO = "BAIXO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"
    CRITICO = "CRITICO"
