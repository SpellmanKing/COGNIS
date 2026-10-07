"""Implementações concretas dos 4 perfis táticos de Iniciação Científica (Subgrupo C)."""
from typing import List, Optional
from cognis.strategies.base import TacticalStrategy
from cognis.domain.enums import ActionType, UrgencyLevel, RiskLevel


class AggressiveStrategy(TacticalStrategy):
    """Perfil Agressivo: Prioriza confronto proativo e avanço sobre posições de ameaça."""

    def __init__(self, directive: Optional[str] = None):
        super().__init__(
            name="Agressivo",
            directive=directive or "Priorize o confronto imediato e avanço sobre posições de ameaça."
        )

    @property
    def risk_tolerance(self) -> RiskLevel:
        return RiskLevel.ALTO

    @property
    def default_urgency(self) -> UrgencyLevel:
        return UrgencyLevel.ALTA

    @property
    def preferred_actions(self) -> List[ActionType]:
        return [ActionType.AVANCAR]

    @property
    def deliberation_focus(self) -> str:
        return "Identificar ameaças e planejar aproximação agressiva ou combate direto."


class DefensiveStrategy(TacticalStrategy):
    """Perfil Defensivo: Prioriza segurança, minimização de dano e fortificação de posições."""

    def __init__(self, directive: Optional[str] = None):
        super().__init__(
            name="Defensivo",
            directive=directive or "Priorize a segurança da posição atual, evitando confrontos e acumulando defesas."
        )

    @property
    def risk_tolerance(self) -> RiskLevel:
        return RiskLevel.BAIXO

    @property
    def default_urgency(self) -> UrgencyLevel:
        return UrgencyLevel.MEDIA

    @property
    def preferred_actions(self) -> List[ActionType]:
        return [ActionType.DEFENDER, ActionType.RECUAR]

    @property
    def deliberation_focus(self) -> str:
        return "Analisar rotas de fuga seguras e estabelecer perímetro de contenção."


class ExplorerStrategy(TacticalStrategy):
    """Perfil Explorador: Prioriza descoberta de pontos cegos e mapeamento sistemático de recursos."""

    def __init__(self, directive: Optional[str] = None):
        super().__init__(
            name="Explorador",
            directive=directive or "Priorize a busca de novos pontos e recursos em áreas desconhecidas do mapa."
        )

    @property
    def risk_tolerance(self) -> RiskLevel:
        return RiskLevel.MEDIO

    @property
    def default_urgency(self) -> UrgencyLevel:
        return UrgencyLevel.BAIXA

    @property
    def preferred_actions(self) -> List[ActionType]:
        return [ActionType.PATRULHAR]

    @property
    def deliberation_focus(self) -> str:
        return "Calcular coordenadas inexploradas para ampliar a visibilidade do mapa."


class OpportunisticStrategy(TacticalStrategy):
    """Perfil Oportunista: Colete recursos com baixo risco; recue imediatamente sob ameaça."""

    def __init__(self, directive: Optional[str] = None):
        super().__init__(
            name="Oportunista",
            directive=directive or "Colete recursos disponíveis quando o risco for baixo; se ameaçado, recue."
        )

    @property
    def risk_tolerance(self) -> RiskLevel:
        return RiskLevel.MEDIO

    @property
    def default_urgency(self) -> UrgencyLevel:
        return UrgencyLevel.MEDIA

    @property
    def preferred_actions(self) -> List[ActionType]:
        return [ActionType.COLETAR_RECURSO, ActionType.RECUAR]

    @property
    def deliberation_focus(self) -> str:
        return "Ponderar proximidade de recursos em relação à distância de ameaças conhecidas."


class DynamicTacticalStrategy(TacticalStrategy):
    """Estratégia configurada dinamicamente via dicionário ou parâmetros customizados."""

    def __init__(
        self,
        name: str,
        directive: str,
        risk_tolerance: RiskLevel = RiskLevel.MEDIO,
        default_urgency: UrgencyLevel = UrgencyLevel.MEDIA,
        preferred_actions: Optional[List[ActionType]] = None,
        deliberation_focus: Optional[str] = None
    ):
        super().__init__(name=name, directive=directive)
        self._risk_tolerance = risk_tolerance
        self._default_urgency = default_urgency
        self._preferred_actions = preferred_actions or [ActionType.PATRULHAR]
        self._deliberation_focus = deliberation_focus or f"Atuação tática sob a diretriz de {name}."

    @property
    def risk_tolerance(self) -> RiskLevel:
        return self._risk_tolerance

    @property
    def default_urgency(self) -> UrgencyLevel:
        return self._default_urgency

    @property
    def preferred_actions(self) -> List[ActionType]:
        return self._preferred_actions

    @property
    def deliberation_focus(self) -> str:
        return self._deliberation_focus
