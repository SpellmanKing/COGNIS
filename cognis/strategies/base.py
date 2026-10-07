"""Interface base e classe abstrata para o padrão Strategy de Perfis Táticos."""
from abc import ABC, abstractmethod
from typing import List
from cognis.domain.enums import ActionType, UrgencyLevel, RiskLevel
from cognis.security.redaction import TacticalMasker


class TacticalStrategy(ABC):
    """Padrão Strategy que encapsula a diretriz tática, postura de risco e deliberação do agente."""

    def __init__(self, name: str, directive: str):
        self._name = name
        self._directive = directive
        # Registra a diretriz no mascarador de segurança do Subgrupo D
        TacticalMasker.get_instance().register_directive(directive)

    @property
    def name(self) -> str:
        """Nome identificador do perfil estratégico."""
        return self._name

    @property
    def directive(self) -> str:
        """Diretriz estratégica confidencial do perfil."""
        return self._directive

    @property
    @abstractmethod
    def risk_tolerance(self) -> RiskLevel:
        """Postura de tolerância ao risco do perfil."""
        pass

    @property
    @abstractmethod
    def default_urgency(self) -> UrgencyLevel:
        """Nível típico de urgência das ações."""
        pass

    @property
    @abstractmethod
    def preferred_actions(self) -> List[ActionType]:
        """Ações prioritárias alinhadas à doutrina do perfil."""
        pass

    @property
    def deliberation_focus(self) -> str:
        """Foco orientador para o preenchimento do Scratchpad (Chain-of-Thought)."""
        return f"Alinhar decisões à doutrina operacional do perfil {self.name}."

    def __repr__(self) -> str:
        # Mascara a diretriz em logs ou impressões acidentais de objetos
        return f"TacticalStrategy(name='{self._name}', directive='[CONFIDENCIAL_SUBGRUPO_D]')"

    def __str__(self) -> str:
        return f"Perfil Tático [{self._name}]"
